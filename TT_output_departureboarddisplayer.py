from __future__ import division
from datetime import datetime, timedelta
from TT_translators_schedules import TimeTranslator
        
class DepartureboardDisplayer(object):

    def __init__(self, data_controllers, group_controller):
        self.timing_point_controller = data_controllers.timing_point_controller
        self.group_controller = group_controller

    def find_relevant_groups(self, timing_point):
        relevant_groups = set()
        for group in self.group_controller:
            if group.is_at(timing_point):
                relevant_groups.add(group)
        return relevant_groups
        
    def count_passenger_trains_per_hour(self, timing_point, relevant_groups):
        trains_per_hour = 0
        stops_per_hour = 0
        passes_per_hour = 0
        groups = set()
        stoppers = set()
        passers = set()
        for group in relevant_groups:
            group.calculate_halts()
            if group.train_type.passenger:
                for node in group.nodes:
                    if node.timing_point == timing_point:
                        groups.add(group.short_headcode.short_headcode_string)
                        trains_per_hour = trains_per_hour + 60/group.frequency
                        if node.halt:
                            stops_per_hour = stops_per_hour + 60/group.frequency
                            stoppers.add(group.short_headcode.short_headcode_string)
                        else:
                            passes_per_hour = passes_per_hour + 60/group.frequency
                            passers.add(group.short_headcode.short_headcode_string)
        return groups, stoppers, passers, trains_per_hour, stops_per_hour, passes_per_hour
        
    def summarise_passenger_trains_per_hour(self, timing_point, relevant_groups):
        groups, stoppers, passers, trains_per_hour, stops_per_hour, passes_per_hour = self.count_passenger_trains_per_hour(timing_point, relevant_groups)
        print '\nThere are %s trains that visit %s every hour.\nThe following %s train groups stop at %s:' % (int(trains_per_hour), timing_point.name, len(stoppers), timing_point.name)
        print ', '.join(stoppers)
        if len(passers) != 0:
            print 'The following %s train groups pass through %s:' % (len(passers), timing_point.name)
            print ', '.join(passers)
                
    def list_subsequent_calls(self, train, given_train_node):
        subsequent_calls = []
        include = False
        for train_node in train.train_nodes:
            if include:
                if train_node.group_node.halt:
                    subsequent_calls.append(train_node.name)
            if train_node == given_train_node:
                include = True
        return subsequent_calls
    
    def list_train_visits(self, timing_point, relevant_groups):
        train_visits = []
        for group in relevant_groups:
            group.create_trains_from_group()
            for train in group.trains:
                train.calculate_timings()
                corresponding_train_nodes = train.train_nodes_corresponding_to_tp(timing_point)
                for train_node in corresponding_train_nodes:
                    subsequent_calls = self.list_subsequent_calls(train, train_node)
                    train_visits.append([train, train_node, subsequent_calls])
        return train_visits

    def make_ordered_list_of_train_visits(self, start_time, finish_time, train_visits):
        ordered_train_visits = []
        enquiry_time = start_time
        while enquiry_time <= finish_time:
            for train, train_node, subsequent_calls in train_visits:
                if train_node.departure == None:
                    if train_node.arrival == enquiry_time:
                        ordered_train_visits.append([train, train_node, subsequent_calls])
                else:
                    if train_node.departure == enquiry_time:
                        ordered_train_visits.append([train, train_node, subsequent_calls])
            enquiry_time = enquiry_time + timedelta(seconds = 30)
        return ordered_train_visits
    
    def display_ordered_train_visits(self, ordered_train_visits, public_choice, arrival_choice):
        time_translator = TimeTranslator()
        for train, train_node, subsequent_calls in ordered_train_visits:
            if train_node.arrival == None:
                arrival_time = '*****'
                if public_choice == 'w':
                    arrival_time = '******'
            elif not train_node.group_node.halt:
                arrival_time = '-----'
                if public_choice == 'w':
                    arrival_time = '------'
            else:
                if public_choice == 'w':
                    arrival_time = time_translator.half_encode(train_node.arrival)
                if public_choice == 'p':
                    arrival_time = time_translator.encode(train_node.public_arrival)
            if train_node.departure == None:
                departure_time = '*****'
                if public_choice == 'w':
                    departure_time = '******'
            else:
                if public_choice == 'w':
                    departure_time = time_translator.half_encode(train_node.departure)
                if public_choice == 'p':
                    departure_time = time_translator.encode(train_node.public_departure)

            pass_or_stop_string = 'passes'
            if train_node.group_node.halt:
                pass_or_stop_string = 'stops'
            platform = train_node.group_node.platform
            if platform == None:
                calling_string = '%s:' % pass_or_stop_string
            else:
                calling_string = '%s on platform %s:' % (pass_or_stop_string, platform)
                
            subsequent_calls_string = ', '.join(subsequent_calls)
            
            if arrival_choice == 'a':
                print arrival_time, departure_time, train.headcode.headcode_string, calling_string, train.train_nodes[0].name, 'to', train.train_nodes[-1].name
                if pass_or_stop_string == 'stops':
                    if subsequent_calls_string == '':
                        print '                     TERMINATES'
                    else:
                        print '                     calling at', subsequent_calls_string
            
            if arrival_choice == 'n' and subsequent_calls_string != '':
                print departure_time, train.headcode.headcode_string, calling_string, train.train_nodes[0].name, 'to', train.train_nodes[-1].name
                if pass_or_stop_string == 'stops':
                    print '                     calling at', subsequent_calls_string
            if arrival_choice == 'a':
                print ''
                    
    def display_departureboard(self):
        name = raw_input('Which location would you like to see the departure board of? ')
        start_time_string = raw_input('Please give a starting time, in the format HH:MM. ')
        finish_time_string = raw_input('Please give a finishing time, in the format HH:MM. ')
        public_choice = raw_input('Hit "p" to see public times or hit "w" to see working times. ')
        arrival_choice = raw_input('Hit "a" to include arrival times or hit "n" not to see them. ')
        
        timing_point = self.timing_point_controller[name]
        time_translator = TimeTranslator()
        start_time = time_translator.decode(start_time_string)
        finish_time = time_translator.decode(finish_time_string)
        
        relevant_groups = self.find_relevant_groups(timing_point)
        train_visits = self.list_train_visits(timing_point, relevant_groups)
        ordered_train_visits = self.make_ordered_list_of_train_visits(start_time, finish_time, train_visits)
        self.display_ordered_train_visits(ordered_train_visits, public_choice, arrival_choice)
        self.summarise_passenger_trains_per_hour(timing_point, relevant_groups)
        
    def count_stops(self):
        stops = set()
        maximum_stops = 0
        for timing_point in self.timing_point_controller:
            relevant_groups = self.find_relevant_groups(timing_point)
            output = self.count_passenger_trains_per_hour(timing_point, relevant_groups)
            trains_per_hour = output[4]
            if trains_per_hour > maximum_stops:
                maximum_stops = int(trains_per_hour)
            stops.add((timing_point, trains_per_hour))
        ordered_stop_list = []
        for i in xrange(maximum_stops + 2):
            for (timing_point, trains_per_hour) in stops:
                if int(trains_per_hour) == i:
                    ordered_stop_list.append((timing_point, trains_per_hour))
        for (timing_point, trains_per_hour) in ordered_stop_list:
            print '%s has %s trains per hour and %s trains per day.' % (timing_point.name, int(trains_per_hour), 24*int(trains_per_hour))
