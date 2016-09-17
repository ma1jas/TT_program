from __future__ import division
from datetime import datetime, timedelta
from TT_translators_schedules import TimeTranslator

class Visit(object):
    
    def __init__(self, train, train_node):
        self.train = train
        self.train_node = train_node
        self.platform = self.train_node.group_node.platform
        self.halt = self.train_node.group_node.halt
        self.caller = False
        self.passer = False
        self.beginner = False
        self.ender = False
        if self.train_node.group_node.start_point:
            self.beginner = True
        elif self.train_node.group_node.finish_point:
            self.ender = True
        elif self.halt:
            self.caller = True
        else:
            self.passer = True
        self.arrival = self.train_node.arrival
        self.departure = self.train_node.departure

class PlatformConstructor(object):
    
    def __init__(self, data_controllers, group_controller, timing_point, start_time, finish_time):
        self.data_controllers = data_controllers
        self.group_controller = group_controller
        self.timing_point = timing_point
        self.start_time, self.finish_time = start_time, finish_time
        self.duration = self.time_to_x(self.finish_time)
        self.time_translator = TimeTranslator()
        self.number_of_platforms = self.timing_point.number_of_platforms
        self.label_size = 'xx-small'
        self.row_proportion = 0.6

        self.find_relevant_groups()
        self.find_train_visits()

    def time_to_x(self, time):
        offset = time - self.start_time
        return offset.seconds / 60

    def top(self, platform_number):
        return self.number_of_platforms - platform_number + 0.5 + 0.5 * self.row_proportion

    def bottom(self, platform_number):
        return self.number_of_platforms - platform_number + 0.5 - 0.5 * self.row_proportion

    def find_relevant_groups(self):
        self.relevant_groups = set()
        for group in self.group_controller:
            if group.is_at(self.timing_point):
                self.relevant_groups.add(group)

    def include_visit(self, visit):
        visit.include = False
        if visit.train_node.arrival is not None:
            if self.start_time - timedelta(seconds = 1800) <= visit.train_node.arrival <= self.finish_time + timedelta(seconds = 1800):
                visit.include = True
        if visit.train_node.departure is not None:
            if self.start_time - timedelta(seconds = 1800) <= visit.train_node.departure <= self.finish_time + timedelta(seconds = 1800):
                visit.include = True
        try:
            visit.platform_number = int(visit.platform)
        except:
            visit.include = False
        
    def find_train_visits(self):
        self.train_visits = []
        for group in self.relevant_groups:
            group.create_trains_from_group()
            for train in group.trains:
                train.calculate_timings()
                corresponding_train_nodes = train.train_nodes_corresponding_to_tp(self.timing_point)
                for train_node in corresponding_train_nodes:
                    visit = Visit(train, train_node)
                    self.include_visit(visit)
                    if visit.include:
                        self.train_visits.append(visit)

    def set_trains_to_be_drawn(self):
        self.black_x = []
        self.black_y = []
        self.coloured_x = {}
        self.coloured_y = {}
        for route_code in self.data_controllers.route_code_controller:
            self.coloured_x[route_code] = []
            self.coloured_y[route_code] = []
        self.left_labels = []
        self.right_labels = []
        for visit in self.train_visits:
            label = visit.train.group.short_headcode.short_headcode_string
            top = self.top(visit.platform_number)
            bottom = self.bottom(visit.platform_number)
            middle = 0.5 * (top + bottom)
            association = visit.train.group.association
            if not visit.beginner:
                arr_x = self.time_to_x(visit.arrival)
                previous_route_code = visit.train_node.group_node.previous_link.route_code
                self.coloured_x[previous_route_code].extend([arr_x, arr_x, None])
                self.coloured_y[previous_route_code].extend([bottom, top, None])
            if not visit.ender:
                dep_x = self.time_to_x(visit.departure)
                next_route_code = visit.train_node.group_node.next_link.route_code
                self.coloured_x[next_route_code].extend([dep_x, dep_x, None])
                self.coloured_y[next_route_code].extend([bottom, top, None])
            if visit.beginner:
                self.black_x.extend([dep_x - association + 1, dep_x, None, dep_x - association + 1, dep_x, None])
                self.black_y.extend([bottom, bottom, None, top, top, None])
                if self.start_time <= visit.departure <= self.finish_time:
                   self.left_labels.append([label, dep_x, middle])
            elif visit.ender:
                self.black_x.extend([arr_x, arr_x + 1, None, arr_x, arr_x + 1, None])
                self.black_y.extend([bottom, bottom, None, top, top, None])
                if self.start_time <= visit.arrival <= self.finish_time:
                    self.right_labels.append([label, arr_x, middle])
            elif visit.caller:
                if self.time_to_x(visit.arrival) <= self.time_to_x(visit.departure):
                    self.black_x.extend([arr_x, dep_x, None, arr_x, dep_x, None])
                    self.black_y.extend([bottom, bottom, None, top, top, None])
                else:
                    self.black_x.extend([0, dep_x, None, 0, dep_x, None])
                    self.black_y.extend([bottom, bottom, None, top, top, None])
                if self.start_time <= visit.departure <= self.finish_time:
                    self.left_labels.append([label, dep_x, middle])
            elif visit.passer:
                self.black_x.extend([dep_x, dep_x, None])
                self.black_y.extend([bottom, top, None])
                if self.start_time <= visit.departure <= self.finish_time:
                    self.left_labels.append([label, dep_x, middle])
           
    def draw_the_trains(self):
        self.set_trains_to_be_drawn()

        self.pyplot.plot(self.black_x, self.black_y, 'k')
        for route_code in self.data_controllers.route_code_controller:
            if len(self.coloured_x[route_code]) > 0:
                self.pyplot.plot(self.coloured_x[route_code], self.coloured_y[route_code], color = route_code.colour)
        for label, x, y in self.left_labels:
            self.pyplot.text(x, y, label, horizontalalignment='left', verticalalignment='center', size = self.label_size)
        for label, x, y in self.right_labels:
            self.pyplot.text(x, y, label, horizontalalignment='right', verticalalignment='center', size = self.label_size)

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
        remainder = (self.start_time.minute)%(self.major_separation)
        xtick = self.major_separation - remainder
        if remainder == 0:
            xtick = 0
        while xtick <= self.duration:
            self.xticks.append(xtick)
            xtick_datetime = self.start_time + timedelta(seconds = 60*xtick)
            xtick_meaning = self.time_translator.encode(xtick_datetime)
            self.xtick_meanings.append(xtick_meaning)
            xtick = xtick + self.major_separation

        self.minor_xticks = []
        minor_xtick = 0
        while minor_xtick <= self.duration:
            if (minor_xtick + remainder) % (self.major_separation) != 0:
                self.minor_xticks.append(minor_xtick)
            minor_xtick = minor_xtick + self.minor_separation

    def make_major_xlines(self):
        self.major_xlines_xcoords = []
        self.major_xlines_ycoords = []
        for xtick in self.xticks:
            self.major_xlines_xcoords.extend([xtick, xtick, None])
            self.major_xlines_ycoords.extend([0, self.number_of_platforms, None])
    
    def make_minor_xlines(self):
        self.minor_xlines_xcoords = []
        self.minor_xlines_ycoords = []
        for minor_xtick in self.minor_xticks:
            self.minor_xlines_xcoords.extend([minor_xtick, minor_xtick, None])
            self.minor_xlines_ycoords.extend([0, self.number_of_platforms, None])
            
    def make_yticks(self):
        self.yticks = []
        self.ytick_meanings = []
        for i in xrange(self.number_of_platforms):
            ytick = i + 0.5
            self.yticks.append(ytick)
            ytick_meaning = self.number_of_platforms - i
            self.ytick_meanings.append(ytick_meaning)
            
    def make_ylines(self):
        self.ylines_xcoords = []
        self.ylines_ycoords = []
        for i in xrange(self.number_of_platforms):
            self.ylines_xcoords.extend([0, self.duration, None])
            self.ylines_ycoords.extend([i + 1, i + 1, None])
                                    
    def produce_graph(self):
        from matplotlib import pyplot # THIS IS HERE, RATHER THAN AT THE TOP, TO FIX A GLITCH WITH MATPLOTLIB FOULING UP RAW INPUTS.
        self.pyplot = pyplot
        # We draw the x- and y- lines.
        self.calculate_separations()
        self.pyplot.figure(figsize=(16,8))
        self.make_xticks()
        self.make_major_xlines()
        self.pyplot.plot(self.major_xlines_xcoords, self.major_xlines_ycoords, '0.7')
        self.make_minor_xlines()
        self.pyplot.plot(self.minor_xlines_xcoords, self.minor_xlines_ycoords, '0.85')
        self.make_yticks()
        self.make_ylines()
        self.pyplot.plot(self.ylines_xcoords, self.ylines_ycoords, '0.85')

        self.draw_the_trains()

        # We draw the axes and x- and y-ticks and labels.
        pyplot.axis([0, self.duration, 0, self.number_of_platforms])
        pyplot.ylabel('platforms')
        pyplot.title(self.timing_point.name)
        pyplot.yticks(self.yticks, self.ytick_meanings)
        pyplot.xticks(self.xticks, self.xtick_meanings)
        pyplot.show()
        
class PlatformShower(object):
    
    def __init__(self, data_controllers, group_controller):
        self.data_controllers = data_controllers
        self.group_controller = group_controller
        
    def show_platforms(self):
        timing_point_name = raw_input('Please give the name of the timing point. ')
        timing_point = self.data_controllers.timing_point_controller[timing_point_name]
#        start_time_string = raw_input('Please give a starting time for the graph, in the format HH:MM. ')
 #       finish_time_string = raw_input('Please give a finishing time for the graph, in the format HH:MM. ')
        start_time_string = '10:00'
        finish_time_string = '11:00'
        time_translator = TimeTranslator()
        start_time = time_translator.decode(start_time_string)
        finish_time = time_translator.decode(finish_time_string)

        platform_constructor = PlatformConstructor(self.data_controllers, self.group_controller, timing_point, start_time, finish_time)
        platform_constructor.produce_graph()
