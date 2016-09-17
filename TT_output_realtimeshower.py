from datetime import datetime, timedelta
from time import sleep
from TT_translators_schedules import TimeTranslator

class RealtimeShower(object):

    def __init__(self, data_controllers, group_controller):
        self.timing_point_controller = data_controllers.timing_point_controller
        self.group_controller = group_controller

    def find_relevant_groups(self, timing_point):
        relevant_groups = set()
        for group in self.group_controller:
            if group.is_at(timing_point):
                relevant_groups.add(group)
        return relevant_groups

    def list_train_visits(self, timing_point, relevant_groups):
        train_visits = []
        for group in relevant_groups:
            group.create_trains_from_group()
            for train in group.trains:
                train.calculate_timings()
                corresponding_train_nodes = train.train_nodes_corresponding_to_tp(timing_point)
                for train_node in corresponding_train_nodes:
                    train_visits.append([train, train_node])
        return train_visits

    def display_visits(self, train_visits, start_time, finish_time, show_passes):
        increment = timedelta(seconds = 1)
        waiting_time = 0.03
        t_0 = start_time
        while t_0 <= finish_time:
            t_1 = t_0 + increment
            for train, train_node in train_visits:
                platform_string = '.'
                if train_node.group_node.platform != None:
                    platform_string = ''.join([' on platform ', train_node.group_node.platform, '.'])
                if train_node.exact_arrival != None and train_node.group_node.halt:
                    if t_0 <= train_node.exact_arrival and train_node.exact_arrival < t_1:
                        time_string = self.time_translator.exact_encode(train_node.exact_arrival)
                        arrival_notice = ''.join([time_string, ': ', train.headcode.headcode_string, ' arrives', platform_string])
                        print arrival_notice
                if train_node.exact_departure != None:
                    if t_0 <= train_node.exact_departure and train_node.exact_departure < t_1:
                        time_string = self.time_translator.exact_encode(train_node.exact_departure)
                        if train_node.group_node.halt:
                            departure_notice = ''.join([time_string, ': ', train.headcode.headcode_string, ' departs', platform_string])
                            print departure_notice
                        else:
                            if show_passes:
                                pass_notice = ''.join([time_string, ': ', train.headcode.headcode_string, ' passes', platform_string])
                                print pass_notice
            t_0 = t_1
            sleep(waiting_time)

    def show_realtime(self):
        name = raw_input('Which location would you like to see the departure board of? ')
        start_time_string = raw_input('Please give a starting time, in the format HH:MM. ')
        finish_time_string = raw_input('Please give a finishing time, in the format HH:MM. ')
        show_passes_string = raw_input('Do you want to show trains that do not stop? Enter "y" for yes and "n" for no. ')

        timing_point = self.timing_point_controller[name]
        self.time_translator = TimeTranslator()
        start_time = self.time_translator.decode(start_time_string)
        finish_time = self.time_translator.decode(finish_time_string) 
        show_passes = True
        if show_passes_string == 'n':
            show_passes = False

        relevant_groups = self.find_relevant_groups(timing_point)
        train_visits = self.list_train_visits(timing_point, relevant_groups)
        self.display_visits(train_visits, start_time, finish_time, show_passes)
