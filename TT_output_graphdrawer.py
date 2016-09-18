from __future__ import division
from datetime import datetime, timedelta
from math import atan, pi
from TT_basics_tools import ZeroBlockMeasurer
from TT_translators_schedules import TimeTranslator

class GraphConstructor(object):

    def __init__(self, route_code_controller, edge_controller, group_controller, line_of_route, graph_start_time, graph_finish_time):
        self.route_code_controller = route_code_controller
        self.edge_controller = edge_controller
        self.group_controller = group_controller
        self.line_of_route = line_of_route
        self.line_of_route.collect_seq_edges(self.edge_controller)
        self.line_of_route.collect_all_edges(self.edge_controller)
        self.line_of_route.make_node_finder()
        self.time_translator = TimeTranslator()
        self.graph_start_time = graph_start_time
        self.graph_finish_time = graph_finish_time
        self.duration = (self.graph_finish_time - self.graph_start_time).seconds/60
        self.label_size = 'xx-small'

    def calculate_separations(self):
        if self.duration <= 90:
            self.minor_separation = 1
            self.major_separation = 5
        elif self.duration <= 180:
            self.minor_separation = 2
            self.major_separation = 10
        elif self.duration <= 270:
            self.minor_separation = 5
            self.major_separation = 15
        else:
            self.minor_separation = 10
            self.major_separation = 30

    def make_xticks(self):
        self.calculate_separations()
        self.xticks = []
        self.xtick_meanings = []
        remainder = (self.graph_start_time.minute)%(self.major_separation)
        xtick = self.major_separation - remainder
        if remainder == 0:
            xtick = 0
        while xtick <= self.duration:
            self.xticks.append(xtick)
            xtick_datetime = self.graph_start_time + timedelta(seconds = 60*xtick)
            xtick_meaning = self.time_translator.encode(xtick_datetime)
            self.xtick_meanings.append(xtick_meaning)
            xtick = xtick + self.major_separation

        self.minor_xticks = []
        minor_xtick = 0
        while minor_xtick <= self.duration:
            if (minor_xtick + remainder)%(self.major_separation) != 0:
                self.minor_xticks.append(minor_xtick)
            minor_xtick = minor_xtick + self.minor_separation

    def make_major_xlines(self):
        self.major_xlines_xcoords = []
        self.major_xlines_ycoords = []
        for xtick in self.xticks:
            self.major_xlines_xcoords.extend([xtick, xtick, None])
            self.major_xlines_ycoords.extend([0, self.line_of_route.total_distance, None])

    def make_minor_xlines(self):
        self.minor_xlines_xcoords = []
        self.minor_xlines_ycoords = []
        for minor_xtick in self.minor_xticks:
            self.minor_xlines_xcoords.extend([minor_xtick, minor_xtick, None])
            self.minor_xlines_ycoords.extend([0, self.line_of_route.total_distance, None])

    def make_yticks(self):
        self.yticks = []
        self.ytick_meanings = []
        for node in self.line_of_route:
            ytick = node.distance_from_start
            self.yticks.append(ytick)
            ytick_meaning = node.timing_point.name
            self.ytick_meanings.append(ytick_meaning)

    def make_ylines(self):
        self.ylines_xcoords = []
        self.ylines_ycoords = []
        for ytick in self.yticks:
            self.ylines_xcoords.extend([0, self.duration, None])
            self.ylines_ycoords.extend([ytick, ytick, None])

    def direct_links_on_graph(self, group):
        links_directions = []
        for link in group.links:
            if link.edge in self.line_of_route.forward_edges:
                links_directions.append(1)
            elif link.edge in self.line_of_route.backward_edges:
                links_directions.append(-1)
            else:
                links_directions.append(0)
        return links_directions

    # We can now introduce a tool that will provide a list of the indices of those links that need headcode labels on the graph. Headcode labels should appear roughly midway along each connected component of the graph. There may be more than one of these, as the train may go off the graph and then re-appear later on in its schedule.
    def where_to_put_headcode_labels(self, group):
        links_directions = self.direct_links_on_graph(group)
        zero_block_measurer = ZeroBlockMeasurer()
        true_block_lengths, false_block_lengths = zero_block_measurer.record_lengths_of_zero_blocks(links_directions)
        number_of_true_blocks = len(true_block_lengths)
        indices_of_links_needing_headcode_labels = []
        total = 0
        for index in xrange(number_of_true_blocks):
            true_block_length = true_block_lengths[index]
            false_block_length = false_block_lengths[index]
            total = total + false_block_length
            index_of_link_needing_headcode_label = int(total + 0.5 * (true_block_length - 1))
            indices_of_links_needing_headcode_labels.append(index_of_link_needing_headcode_label)
            total = total + true_block_length
        return indices_of_links_needing_headcode_labels

    # We introduce methods that append coordinates and other information to the aforementioned lists or dictionaries. Then we can draw them all en masse at the end.
    def set_leg_to_be_drawn(self, time_1, time_2, mileage_1, mileage_2, route_code):
        leg_xcoord = [time_1, time_2, None]
        leg_ycoord = [mileage_1, mileage_2, None]
        self.legs_xcoords[route_code].extend(leg_xcoord)
        self.legs_ycoords[route_code].extend(leg_ycoord)

    def set_terminus_item_to_be_drawn(self, time, mileage, route_code):
        terminus_xcoord = [time, None]
        terminus_ycoord = [mileage, None]
        self.termini_xcoords[route_code].extend(terminus_xcoord)
        self.termini_ycoords[route_code].extend(terminus_ycoord)

    def set_half_adjustment_item_to_be_drawn(self, time, mileage):
        position = [time, mileage]
        self.half_adjustment_labels.append(position)

    def set_pathing_item_to_be_drawn(self, time, mileage, pathing):
        pathing_string = ''.join(['(', str(pathing), ')'])
        position = [time, mileage]
        self.pathing_labels.append([pathing_string, position])

    def set_headcode_item_to_be_drawn(self, time_1, time_2, mileage_1, mileage_2, headcode):
        xcoord = 0.5*(time_1 + time_2)
        ycoord = 0.5*(mileage_1 + mileage_2)
        if time_1 != time_2:
            rotation_value = (140/pi)*atan((mileage_2 - mileage_1)*self.duration/((time_2 - time_1)*self.line_of_route.total_distance))
        elif mileage_1 < mileage_2:
            rotation_value = 90
        else:
            rotation_value = -90
        if rotation_value > 0:
            xcoord = xcoord - (self.duration)/40.0
        position = [xcoord, ycoord]
        self.headcode_labels.append([headcode.headcode_string, position, rotation_value])

    def set_train_link_to_be_drawn(self, group, train, offset, link_index, draw_link, draw_next_link, headcode_label_needed):
        train_node_A = train.train_nodes[link_index]
        train_node_B = train.train_nodes[link_index + 1]
        link = group.links[link_index]
        time_A_departure = offset + train_node_A.group_node.rounded_departure
        time_B_arrival = offset + train_node_B.group_node.rounded_arrival
        mileage_A = self.line_of_route.node_finder[train_node_A.group_node.timing_point].distance_from_start
        if draw_link == 1:
            mileage_A = mileage_A + self.line_of_route.total_distance/1200
        if draw_link == -1:
            mileage_A = mileage_A - self.line_of_route.total_distance/400
        mileage_B = self.line_of_route.node_finder[train_node_B.group_node.timing_point].distance_from_start
        if draw_link == 1:
            mileage_B = mileage_B + self.line_of_route.total_distance/1200
        if draw_link == -1:
            mileage_B = mileage_B - self.line_of_route.total_distance/400

        # We set the journey leg to be drawn.
        self.set_leg_to_be_drawn(time_A_departure, time_B_arrival, mileage_A, mileage_B, link.route_code)

        # We set a pathing label to be drawn if the link has non-None pathing value.
        if link.pathing != None:
            if mileage_B != 0:
                mileage = mileage_B
            else:
                mileage = 0.00001 # THIS FIXES A GLITCH WITH MATPLOTLIB.
            self.set_pathing_item_to_be_drawn(time_B_arrival, mileage, link.pathing)

        # We set a headcode label to be drawn if the current link is roughly midway along the current connected component of the schedule. (This is an attempt to spread the headcode labels of different groups' trains out a bit.)
        if headcode_label_needed:
            self.set_headcode_item_to_be_drawn(time_A_departure, time_B_arrival, mileage_A, mileage_B, train.headcode)

        # If the train starts at point A, then we set a terminus label to be drawn.
        if train_node_A.group_node.start_point:
            route_code = link.route_code
            if train_node_A.group_node.timing_point.platform_routes[train_node_A.group_node.platform] is not None:
                route_code = train_node_A.group_node.timing_point.platform_routes[train_node_A.group_node.platform]
            self.set_terminus_item_to_be_drawn(time_A_departure, mileage_A, route_code)
        # Otherwise, if the train has an intermediate stop at point A, then we set its stop there to be drawn.
        else:
            if train_node_A.group_node.halt:
                time_A_arrival = offset + train_node_A.group_node.rounded_arrival
                route_code = train_node_A.group_node.route_code
                self.set_leg_to_be_drawn(time_A_arrival, time_A_departure, mileage_A, mileage_A, route_code)

        # If the train finishes at point B, then we set a terminus label to be drawn.
        if train_node_B.group_node.finish_point:
            route_code = link.route_code
            if train_node_B.group_node.timing_point.platform_routes[train_node_B.group_node.platform] is not None:
                route_code = train_node_B.group_node.timing_point.platform_routes[train_node_B.group_node.platform]
            self.set_terminus_item_to_be_drawn(time_B_arrival, mileage_B, route_code)
            # We also set a half-adjustment label to be drawn, if the train is adjusted by 0.5 minutes to finish on a whole minute.
            if group.half_adjustment:
                if mileage_B == 0:
                    mileage = 0.00001
                elif mileage_B >= self.line_of_route.total_distance:
                    mileage = self.line_of_route.total_distance - 0.00001
                else:
                    mileage = mileage_B
                    # THIS FIXES A GLITCH WITH MATPLOTLIB REGARDING MISSING ANNOTATIONS ON THE X-AXIS.
                self.set_half_adjustment_item_to_be_drawn(time_B_arrival, mileage)

        # Otherwise, if the train has an intermediate stop at point B, and if the train leaves the graph after point B, then we set its stop there to be drawn, otherwise it will be left out.
        elif draw_next_link == 0:
            if train_node_B.group_node.halt:
                time_B_departure = offset + train_node_B.group_node.rounded_departure
                route_code = train_node_B.group_node.route_code
                if route_code is None:
                    print 'Train %s has no route code at %s.' % (group.short_headcode.short_headcode_string, train_node_B.group_node.timing_point.name)
                self.set_leg_to_be_drawn(time_B_arrival, time_B_departure, mileage_B, mileage_B, route_code)

    def set_train_to_be_drawn(self, group, links_directions, train, indices_of_links_needing_headcode_labels):
        offset_time = train.start_time - self.graph_start_time
        offset = (offset_time.days)*1440 + (offset_time.seconds)/60.0
        for link_index, _ in enumerate(group.links):
            draw_link = links_directions[link_index]
            if link_index != len(group.links) - 1:
                draw_next_link = links_directions[link_index + 1]
            if draw_link != 0:
                headcode_label_needed = (link_index in indices_of_links_needing_headcode_labels)
                self.set_train_link_to_be_drawn(group, train, offset, link_index, draw_link, draw_next_link, headcode_label_needed)

    def set_trains_to_be_drawn(self):
        self.legs_xcoords = {}
        self.legs_ycoords = {}
        self.termini_xcoords = {}
        self.termini_ycoords = {}
        self.headcode_labels = []
        self.pathing_labels = []
        self.half_adjustment_labels = []
        for route_code in self.route_code_controller:
            self.legs_xcoords[route_code] = []
            self.legs_ycoords[route_code] = []
            self.termini_xcoords[route_code] = []
            self.termini_ycoords[route_code] = []
        for group in self.group_controller:
            if group.is_group_on_line_of_route(self.line_of_route):
                group.create_trains_from_group()
                links_directions = self.direct_links_on_graph(group)
                indices_of_links_needing_headcode_labels = self.where_to_put_headcode_labels(group)
                for train in group.trains:
                    if train.start_time < self.graph_finish_time and train.finish_time > self.graph_start_time:
                        self.set_train_to_be_drawn(group, links_directions, train, indices_of_links_needing_headcode_labels)

    def draw_the_trains(self):
        from matplotlib import pyplot # THIS IS HERE, RATHER THAN AT THE TOP, TO FIX A GLITCH WITH MATPLOTLIB FOULING UP RAW INPUTS.
        self.set_trains_to_be_drawn()
        for route_code in self.route_code_controller:
            # For drawing legs, we only need to use the colours of those route codes that are actually used by some schedule.
            if len(self.legs_xcoords[route_code]) > 0:
                pyplot.plot(self.legs_xcoords[route_code], self.legs_ycoords[route_code], color = route_code.colour)
            # For drawing terminus labels, we only need to use the colours of those route codes that are actually used by some schedule leaving its origin or approaching its destination. We use a diamond shape.
            if len(self.termini_xcoords[route_code]) > 0:
                pyplot.plot(self.termini_xcoords[route_code], self.termini_ycoords[route_code], color = route_code.colour, marker = 'd')
        for pathing_string, position in self.pathing_labels:
            pyplot.annotate(pathing_string, position, size = self.label_size)
            pyplot.plot(position[0], position[1], color = 'k', marker = '*')
        for position in self.half_adjustment_labels:
            pyplot.annotate('{0.5}', position, size = self.label_size)
            pyplot.plot(position[0], position[1], color = 'k', marker = '')
        for headcode_string, position, rotation_value in self.headcode_labels:
            pyplot.annotate(headcode_string, position, rotation = rotation_value, size = self.label_size)

    def produce_graph(self, show, save):
        from matplotlib import pyplot # THIS IS HERE, RATHER THAN AT THE TOP, TO FIX A GLITCH WITH MATPLOTLIB FOULING UP RAW INPUTS.
        # We draw the x- and y- lines.
        self.calculate_separations()
        pyplot.figure(figsize=(16,8))
        self.make_xticks()
        self.make_major_xlines()
        pyplot.plot(self.major_xlines_xcoords, self.major_xlines_ycoords, '0.50')
        self.make_minor_xlines()
        pyplot.plot(self.minor_xlines_xcoords, self.minor_xlines_ycoords, '0.75')
        self.make_yticks()
        self.make_ylines()
        pyplot.plot(self.ylines_xcoords, self.ylines_ycoords, '0.75')

        # We draw the trains. We only do this AFTER the previous step, to ensure that trains are drawn over the x- and y-lines.
        self.draw_the_trains()

        # We draw the axes and x- and y-ticks and labels.
        pyplot.axis([0, self.duration, -0.05, self.line_of_route.total_distance])
        pyplot.title(self.line_of_route.name)
        pyplot.yticks(self.yticks, self.ytick_meanings)
        second_axis = pyplot.twinx()
        pyplot.xticks(self.xticks, self.xtick_meanings)
        second_axis.set_yticks(self.yticks)
        second_axis.set_yticklabels(self.yticks)
        second_axis.set_ylabel('mileage')

        graph_screenshot_filename = ''.join(['../TT_graphs/graph', str(self.line_of_route.number), '.png'])
        if len(str(self.line_of_route.number)) == 1:
            graph_screenshot_filename = ''.join(['../TT_graphs/graph0', str(self.line_of_route.number), '.png'])
        if save:
            pyplot.savefig(graph_screenshot_filename, bbox_inches='tight')
        if show:
            pyplot.show()
        else:
            pyplot.clf() # This means "clear figure".

class GraphDrawer(object):

    def __init__(self, data_controllers, group_controller):
        self.data_controllers = data_controllers
        self.group_controller = group_controller

    def draw_graph(self, choice):
        if choice == 'g':
            line_of_route_number = input('Which line of route would you like to see the graph of? ')
            graph_start_time_string = raw_input('Please give a starting time for the graph, in the format HH:MM. ')
            graph_finish_time_string = raw_input('Please give a finishing time for the graph, in the format HH:MM. ')
            save = False
        elif choice == 'j':
            graph_start_time_string = '12:00'
            graph_finish_time_string = '12:45'
            save = True
        else:
            line_of_route_number = int(choice[1:])
            graph_start_time_string = '12:00'
            if choice[0] == 'f':
                graph_finish_time_string = '12:30'
                save = False
            if choice[0] == 't':
                graph_finish_time_string = '12:45'
                save = True
            if choice[0] == 'h':
                graph_finish_time_string = '13:00'
                save = False
        time_translator = TimeTranslator()
        graph_start_time = time_translator.decode(graph_start_time_string)
        graph_finish_time = time_translator.decode(graph_finish_time_string)

        if choice != 'j':
            line_of_route = self.data_controllers.line_of_route_controller[line_of_route_number]
            graph_constructor = GraphConstructor(self.data_controllers.route_code_controller, self.data_controllers.edge_controller, self.group_controller, line_of_route, graph_start_time, graph_finish_time)
            graph_constructor.produce_graph(True, save)
        if choice == 'j':
            for line_of_route in self.data_controllers.line_of_route_controller:
                graph_constructor = GraphConstructor(self.data_controllers.route_code_controller, self.data_controllers.edge_controller, self.group_controller, line_of_route, graph_start_time, graph_finish_time)
                print ''.join(['Done graph number ', str(line_of_route.number), '.'])
                graph_constructor.produce_graph(False, True)
