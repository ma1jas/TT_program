from __future__ import division
from TT_translators_schedules import TimeTranslator

from datetime import datetime, timedelta
from time import sleep
import sys, pygame

class Locator(object):

    def __init__(self, pixels_per_mile):
        self.pixels_per_mile = pixels_per_mile
        self.pixels_per_eighth_mile = pixels_per_mile / 8

    def interpolate(self, parameter, value_0, value_1):
        return (1 - parameter) * value_0 + parameter * value_1

    def scale_in(self, x, x_0, x_1, value_0, value_1):
        parameter = (x - x_0) / (x_1 - x_0)
        return self.interpolate(parameter, value_0, value_1)

    def scale_in_2d(self, x, x_0, x_1, coordinate_0, coordinate_1):
        return (self.scale_in(x, x_0, x_1, coordinate_0[0], coordinate_1[0]), self.scale_in(x, x_0, x_1, coordinate_0[1], coordinate_1[1]))

    def locate(self, t, group_link, train_type):
        speed_profile = group_link.speed_profile
        pathing = group_link.pathing
        if pathing != None:
            t = t * speed_profile.srt/(pathing + speed_profile.srt)
        acc = train_type.acceleration
        dec = train_type.deceleration
        if t < speed_profile.acc_time:
            location = speed_profile.initial_speed * t + 0.5 * acc * (t ** 2)
        elif t < speed_profile.srt - speed_profile.dec_time:
            location = speed_profile.acc_distance + speed_profile.achieved_speed * (t - speed_profile.acc_time)
        else:
            location = speed_profile.distance - speed_profile.final_speed*(speed_profile.srt - t) - 0.5 * dec * ((speed_profile.srt - t) ** 2)
        return location

    def locate_and_scale(self, t, group_link, train_type, vis_link, begin_coords, end_coords):
        location_along_link = self.locate(t, group_link, train_type)
        link_length = vis_link.scene_link.length
        return self.scale_in_2d(location_along_link, 0, link_length, begin_coords, end_coords)

    def locate_in_traversing(self, current_time, traversing, begin_coords, end_coords):
        t = (current_time - traversing.start_time).seconds/60
        group_link = traversing.group_link
        train_type = traversing.train.group.train_type
        (x, y) = self.locate_and_scale(t, group_link, train_type, traversing.vis_link, begin_coords, end_coords)
        if traversing.forwards:
            if begin_coords[0] <= x and x <= begin_coords[0] + self.pixels_per_eighth_mile:
                y = self.scale_in(x, begin_coords[0], begin_coords[0] + self.pixels_per_eighth_mile, y + traversing.begin_y_jump, y)
            if end_coords[0] >= x and x >= end_coords[0] - self.pixels_per_eighth_mile:
                y = self.scale_in(x, end_coords[0] - self.pixels_per_eighth_mile, end_coords[0], y, y + traversing.end_y_jump)
        else:
            if end_coords[0] <= x and x <= end_coords[0] + self.pixels_per_eighth_mile:
                y = self.scale_in(x, end_coords[0], end_coords[0] + self.pixels_per_eighth_mile, y + traversing.end_y_jump, y)
            if begin_coords[0] >= x and x >= begin_coords[0] - self.pixels_per_eighth_mile:
                y = self.scale_in(x, begin_coords[0] - self.pixels_per_eighth_mile, begin_coords[0], y, y + traversing.begin_y_jump)
        return (x, y)

    def y_shift(self, coordinate, y):
        return (coordinate[0], coordinate[1] + y)

    def int_coords(self, coordinate):
        return (int(coordinate[0]), int(coordinate[1]))

class VisNode(object):

    def __init__(self, scene_node):
        self.scene_node = scene_node

class VisLink(object):

    def __init__(self, scene_link):
        self.scene_link = scene_link

class Visiting(object):

    def __init__(self, train, group_node, start_time, finish_time, vis_node):
        self.train = train
        self.group_node = group_node
        self.start_time = start_time
        self.finish_time = finish_time
        self.vis_node = vis_node
        self.platform = group_node.platform
        self.start_point = False
        self.finish_point = False
        self.end_point = False
        self.waiting_point = False

    def locate(self, track_width, locator):
        platform_location = self.vis_node.scene_node.platform_locations[self.platform][0]
        coords = locator.y_shift(self.vis_node.coords, track_width * platform_location)
        return coords

class Calling(Visiting):

    def __init__(self, train, group_node, start_time, finish_time, vis_node):
        Visiting.__init__(self, train, group_node, start_time, finish_time, vis_node)
        self.halt = True

class Passing(Visiting):

    def __init__(self, train, group_node, start_time, finish_time, vis_node):
        Visiting.__init__(self, train, group_node, start_time, finish_time, vis_node)
        self.halt = False

class Traversing(object):

    def __init__(self, train, group_link, start_time, finish_time, vis_link, forwards):
        self.train = train
        self.group_link = group_link
        self.start_time = start_time
        self.finish_time = finish_time
        self.vis_link = vis_link
        self.route_code = self.group_link.route_code
        self.forwards = forwards
        self.begin_y_jump = 0
        self.end_y_jump = 0

    def locate(self, forwards, track_width, locator):
        route_location = self.vis_link.scene_link.route_locations[self.route_code, self.forwards][0]
        if forwards:
            begin_coords = locator.y_shift(self.vis_link.begin_coords, track_width * route_location[0])
            end_coords = locator.y_shift(self.vis_link.end_coords, track_width * route_location[1])
        else:
            begin_coords = locator.y_shift(self.vis_link.end_coords, track_width * route_location[1])
            end_coords = locator.y_shift(self.vis_link.begin_coords, track_width * route_location[0])
        return begin_coords, end_coords

class NodeTrainEvent(object):

    def __init__(self):
        self.visit = None
        self.inward = None
        self.outward = None

    def record_event(self, event, event_type):
        if event_type == 'visit':
            self.visit = event
        if event_type == 'inward':
            self.inward = event
        if event_type == 'outward':
            self.outward = event

class NodeTrainEvents(object):

    def __init__(self):
        self.platform_starts = {}
        self.platform_finishes = {}
        self.non_platforms = {}

    def record_event(self, event, event_type, platform):
        if platform:
            start_time, finish_time = None, None
            if event_type == 'inward':
                start_time = event.finish_time
            if event_type == 'outward':
                finish_time = event.start_time
            if event_type == 'visit':
                start_time = event.start_time
                finish_time = event.finish_time
            if start_time != None:
                if start_time not in self.platform_starts:
                    self.platform_starts[start_time] = NodeTrainEvent()
                self.platform_starts[start_time].record_event(event, event_type)
            if finish_time != None:
                if finish_time not in self.platform_finishes:
                    self.platform_finishes[finish_time] = NodeTrainEvent()
                self.platform_finishes[finish_time].record_event(event, event_type)
        else:
            if event_type == 'inward':
                passing_time = event.finish_time
            if event_type == 'outward':
                passing_time = event.start_time
            if passing_time not in self.non_platforms:
                self.non_platforms[passing_time] = NodeTrainEvent()
            self.non_platforms[passing_time].record_event(event, event_type)

class NodeTrains(object):

    def __init__(self, vis_node):
        self.vis_node = vis_node
        self.trains = {}

    def __setitem__(self, key, value):
        self.trains[key] = value

    def __getitem__(self, key):
        if key in self.trains:
            return self.trains[key]

    def __iter__(self):
        return self.trains.iterkeys()

    def record_event(self, train, event, event_type, platform):
        if train not in self.trains:
            self.trains[train] = NodeTrainEvents()
        self.trains[train].record_event(event, event_type, platform)

class Visualisation(object):

    def __init__(self, scene, start_time, finish_time, size, reload_time, group_controller):
        self.scene = scene
        self.group_controller = group_controller
        self.scene.set_up_scene(self.group_controller)
        self.width, self.height = size
        self.pixels_per_mile = self.width / self.scene.total_distance
        self.track_width = self.height * min(0.04, 1 / (self.scene.y_max + 1))
        self.start_time = start_time
        self.finish_time = finish_time
        self.reload_time = reload_time
        self.cycle_time = (self.reload_time.seconds + self.reload_time.microseconds / 1000000) / (8 * self.scene.total_distance)
        self.cycle_time = 1.0/90
        self.locator = Locator(self.pixels_per_mile)
        self.time_translator = TimeTranslator()
        self.set_colours()

    def set_colours(self):
        self.colours = {}
        self.colours['white'] = pygame.Color('#ffffff')
        self.colours['green'] = pygame.Color('#00ff00')
        self.colours['red'] = pygame.Color('#ff0000')
        self.colours['black'] = pygame.Color('#000000')
        self.colours['grey'] = pygame.Color('#7f7f7f')
        self.colours['yellow'] = pygame.Color('#ffff00')
        self.route_colours = {}

    def find_trains(self):
        self.trains = []
        for group in self.scene.scene_groups:
            group.create_trains_from_group()
            for train in group.trains:
                if train.start_time <= self.finish_time:
                    if train.finish_time >= self.start_time:
                        train.calculate_timings()
                        self.trains.append(train)

    def find_vis_nodes_and_links(self):
        self.vis_nodes = []
        vis_node_finder = {}
        for scene_node in self.scene.scene_nodes:
            vis_node = VisNode(scene_node)
            x = self.width * self.locator.scale_in(scene_node.location[0], 0, self.scene.total_distance, 0.02, 0.94)
            y = self.track_width * scene_node.y
            vis_node.coords = (x, y)
            vis_node.text = scene_node.timing_point.name
            self.vis_nodes.append(vis_node)
            vis_node_finder[scene_node] = vis_node

        for vis_node in self.vis_nodes:
            vis_node.node_trains = NodeTrains(vis_node)

        self.vis_links = []
        for scene_link in self.scene.scene_links:
            vis_link = VisLink(scene_link)
            vis_link.begin_vis_node = vis_node_finder[scene_link.begin_scene_node]
            vis_link.end_vis_node = vis_node_finder[scene_link.end_scene_node]
            vis_link.begin_coords = vis_link.begin_vis_node.coords
            vis_link.end_coords = vis_link.end_vis_node.coords
            self.vis_links.append(vis_link)

    def find_visitings(self):
        self.callings = []
        self.passings = []
        for train in self.trains:
            for train_node in train.train_nodes:
                group_node = train_node.group_node
                for vis_node in self.vis_nodes:
                    if group_node.timing_point == vis_node.scene_node.timing_point:
                        if group_node.platform in vis_node.scene_node.platforms:
                            start_time = train_node.exact_arrival
                            finish_time = train_node.exact_departure
                            if group_node.start_point:
                                start_time = finish_time - timedelta(seconds=train.group.association*60-60)
                            if group_node.finish_point:
                                finish_time = start_time + timedelta(seconds=60)
                            if group_node.halt:
                                calling = Calling(train, group_node, start_time, finish_time, vis_node)
                                calling.coords = calling.locate(self.track_width, self.locator)
                                self.callings.append(calling)
                                vis_node.node_trains.record_event(train, calling, 'visit', True)
                                if group_node.end_point:
                                    calling.end_point = True
                                if group_node.start_point:
                                    calling.start_point = True
                                if group_node.finish_point:
                                    calling.finish_point = True
                            if group_node.start_point:
                                start_time = train_node.exact_departure - timedelta(seconds=train.group.association*60-60)
                                finish_time = train_node.exact_departure - timedelta(seconds=60)
                                calling = Calling(train, group_node, start_time, finish_time, vis_node)
                                calling.coords = calling.locate(self.track_width, self.locator)
                                self.callings.append(calling)
                                vis_node.node_trains.record_event(train, calling, 'visit', True)
                                calling.waiting_point = True
                            else:
                                passing = Passing(train, group_node, start_time, finish_time, vis_node)
                                passing.coords = passing.locate(self.track_width, self.locator)
                                self.passings.append(passing)
                                vis_node.node_trains.record_event(train, passing, 'visit', True)

    def find_traversings(self):
        self.traversings = []
        for train in self.trains:
            previous_train_node = None
            for next_train_node in train.train_nodes:
                if previous_train_node != None:
                    group_link = previous_train_node.group_node.next_link
                    for vis_link in self.vis_links:
                        if group_link.edge == vis_link.scene_link.edge or group_link.edge == vis_link.scene_link.reverse_edge:
                            forwards = True
                            if group_link.edge == vis_link.scene_link.reverse_edge:
                                forwards = False
                            if (group_link.route_code, forwards) in vis_link.scene_link.routes:
                                start_time = previous_train_node.exact_departure
                                finish_time = next_train_node.exact_arrival
                                traversing = Traversing(train, group_link, start_time, finish_time, vis_link, forwards)
                                traversing.begin_coords, traversing.end_coords = traversing.locate(forwards, self.track_width, self.locator)
                                self.traversings.append(traversing)
                                begin_platform, end_platform = False, False
                                if forwards:
                                    if group_link.previous_node.platform in vis_link.begin_vis_node.scene_node.platforms:
                                        begin_platform = True
                                    if group_link.next_node.platform in vis_link.end_vis_node.scene_node.platforms:
                                        end_platform = True
                                    vis_link.begin_vis_node.node_trains.record_event(train, traversing, 'outward', begin_platform)
                                    vis_link.end_vis_node.node_trains.record_event(train, traversing, 'inward', end_platform)
                                else:
                                    if group_link.previous_node.platform in vis_link.end_vis_node.scene_node.platforms:
                                        begin_platform = True
                                    if group_link.next_node.platform in vis_link.begin_vis_node.scene_node.platforms:
                                        end_platform = True
                                    vis_link.end_vis_node.node_trains.record_event(train, traversing, 'outward', begin_platform)
                                    vis_link.begin_vis_node.node_trains.record_event(train, traversing, 'inward', end_platform)
                previous_train_node = next_train_node

    def check_y_jumps(self):
        for vis_node in self.vis_nodes:
            for train in vis_node.node_trains:
                platform_starts = vis_node.node_trains[train].platform_starts
                for time in platform_starts:
                    node_event = platform_starts[time]
                    if node_event.inward != None and node_event.visit != None:
                        inward_y = node_event.inward.end_coords[1]
                        visit_y = node_event.visit.coords[1]
                        if inward_y != visit_y:
                            node_event.inward.end_y_jump = visit_y - inward_y
                platform_finishes = vis_node.node_trains[train].platform_finishes
                for time in platform_finishes:
                    node_event = platform_finishes[time]
                    if node_event.outward != None and node_event.visit != None:
                        outward_y = node_event.outward.begin_coords[1]
                        visit_y = node_event.visit.coords[1]
                        if outward_y != visit_y:
                            node_event.outward.begin_y_jump = visit_y - outward_y
                non_platforms = vis_node.node_trains[train].non_platforms
                for time in non_platforms:
                    node_event = non_platforms[time]
                    if node_event.outward != None and node_event.inward != None:
                        outward_y = node_event.outward.begin_coords[1]
                        inward_y = node_event.inward.end_coords[1]
                        if outward_y != inward_y:
                            node_event.outward.begin_y_jump = (inward_y - outward_y)/2
                            node_event.inward.end_y_jump = (outward_y - inward_y)/2

    def set_up_visualisation(self):
        self.find_trains()
        self.find_vis_nodes_and_links()
        self.find_visitings()
        self.find_traversings()
        self.check_y_jumps()

    def draw_lines(self, pygame, screen):
        for vis_link in self.vis_links:
            (x_begin, y_begin), (x_end, y_end) = vis_link.begin_coords, vis_link.end_coords
            for route_code, forwards in vis_link.scene_link.route_locations:
                show_route = vis_link.scene_link.route_locations[route_code, forwards][1]
                if show_route:
                    route_location = vis_link.scene_link.route_locations[route_code, forwards]
                    begin_offset = self.track_width * route_location[0][0]
                    end_offset = self.track_width * route_location[0][1]
                    begin_coords = self.locator.y_shift(vis_link.begin_coords, begin_offset)
                    end_coords = self.locator.y_shift(vis_link.end_coords, end_offset)
                    if route_code not in self.route_colours:
                        if route_code.name == 'XL':
                            self.route_colours[route_code] = self.colours['grey']
                        elif route_code.name == '_':
                            self.route_colours[route_code] = self.colours['white']
                        else:
                            self.route_colours[route_code] = pygame.Color(route_code.colour)
                    pygame.draw.line(screen, self.route_colours[route_code], self.locator.int_coords(begin_coords), self.locator.int_coords(end_coords))

    def blit_texts(self, pygame, screen, current_time, font, small_font):
        text = font.render(self.time_translator.exact_encode(current_time), 1, self.colours['yellow'])
        time_coords = (self.width * 0.02, self.height * 0.02)
        screen.blit(text, self.locator.int_coords(time_coords))

        for vis_node in self.vis_nodes:
            text = small_font.render(vis_node.text, 1, self.colours['white'])
            node_coords = vis_node.coords
            screen.blit(text, self.locator.int_coords(node_coords))

            for platform in vis_node.scene_node.platforms:
                show_platform_name = vis_node.scene_node.platform_locations[platform][1]
                if show_platform_name:
                    platform_text = small_font.render(str(platform), 1, self.colours['white'])
                    platform_offset = self.track_width * vis_node.scene_node.platform_locations[platform][0]
                    platform_coords = self.locator.y_shift(node_coords, platform_offset)
                    screen.blit(platform_text, self.locator.int_coords(platform_coords))

            for dot_location in vis_node.scene_node.dot_locations:
                dot_text = small_font.render('.', 1, self.colours['white'])
                dot_offset = self.track_width * dot_location
                dot_coords = self.locator.y_shift(node_coords, dot_offset)
                screen.blit(dot_text, self.locator.int_coords(dot_coords))

        for calling in self.callings:
            if calling.start_time < current_time + self.reload_time and calling.finish_time > current_time:
                colour = self.colours['white']
                if calling.start_point:
                    colour = self.colours['green']
                if calling.finish_point:
                    colour = self.colours['red']
                if calling.waiting_point:
                    colour = self.colours['grey']
                text = font.render(calling.train.headcode.headcode_string, 1, colour)
                screen.blit(text, self.locator.int_coords(calling.coords))
                pygame.draw.circle(screen, colour, self.locator.int_coords(calling.coords), 3)

        for traversing in self.traversings:
            if traversing.start_time < current_time and traversing.finish_time > current_time:
                text = font.render(traversing.train.headcode.headcode_string, 1, self.colours['white'])
                in_traversing_coords = self.locator.locate_in_traversing(current_time, traversing, traversing.begin_coords, traversing.end_coords)
                screen.blit(text, self.locator.int_coords(in_traversing_coords))
                pygame.draw.circle(screen, self.colours['white'], self.locator.int_coords(in_traversing_coords), 3)

    def show_visualisation(self):
        self.set_up_visualisation()

        screen = pygame.display.set_mode((self.width, self.height))
        pygame.init()
        font, small_font = pygame.font.Font(None, int(0.015 * self.width)), pygame.font.Font(None, int(0.01 * self.width))

        current_time = self.start_time
        count = 0
        processing_percentage = 0
        while True:
            real_time_start = datetime.now()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print ''.join(['The program ran at ', str(int(100 * processing_percentage / count)), '% capacity.'])
                    sys.exit()
            if current_time > self.finish_time:
                print ''.join(['The program ran at ', str(int(100 * processing_percentage / count)), '% capacity.'])
                sys.exit()

            screen.fill(self.colours['black'])
            self.draw_lines(pygame, screen)
            self.blit_texts(pygame, screen, current_time, font, small_font)

            pygame.display.flip()
            current_time = current_time + self.reload_time
            count = count + 1

            real_time_finish = datetime.now()
            processing_time = (real_time_finish - real_time_start).seconds + (real_time_finish - real_time_start).microseconds / 1000000
            sleep_time = max(0, self.cycle_time - processing_time)
            processing_percentage = processing_percentage + processing_time / self.cycle_time
            sleep(sleep_time)

        sys.exit()

class Visualiser(object):

    def __init__(self, data_controllers, group_controller):
        self.data_controllers = data_controllers
        self.group_controller = group_controller

    def show_visualisation(self):
        scene_number = input('Which scene would you like to see a visualisation of? ')
 #       start_time_string = raw_input('Please give a starting time for the visualisation, in the format HH:MM. ')
  #      finish_time_string = raw_input('Please give a finishing time for the visualisation, in the format HH:MM. ')
        start_time_string, finish_time_string = '10:00', '11:00'
        size = [1300, 700]
        reload_time = timedelta(seconds = 0.5) # Show the state of the timetable every x seconds
        time_translator = TimeTranslator()
        start_time, finish_time = time_translator.decode(start_time_string), time_translator.decode(finish_time_string)
        scene = self.data_controllers.scene_controller[scene_number]
        visualisation = Visualisation(scene, start_time, finish_time, size, reload_time, self.group_controller)
        visualisation.show_visualisation()
