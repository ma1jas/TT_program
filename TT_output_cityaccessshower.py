from __future__ import division
from datetime import datetime, timedelta
from TT_translators_schedules import TimeTranslator
        
class CityaccessShower(object):

    def __init__(self, data_controllers, group_controller):
        self.timing_point_controller = data_controllers.timing_point_controller
        self.group_controller = group_controller

    def show_cityaccess(self):
        for group in self.group_controller:       
            self.assign_city_info(group)
        for timing_point in self.timing_point_controller:
            if timing_point.type == 's':
                if timing_point.city_time is not None and 25 < timing_point.city_time < 100:
                    print timing_point.name, timing_point.city_time

    def assign_city_info(self, group):
        if group.train_type.passenger:
            group.do_basic_calculations()
            count = None
            for node in group.nodes:
                if node.halt:
                    if node.timing_point.city and not node.finish_point:
                        count = 0
                        node.timing_point.city_time = 0
                        start_time = node.rounded_departure
                    if count is not None:
                        if node.timing_point.city_calls is None or node.timing_point.city_calls > count:
                            node.timing_point.city_calls = count
                            node.timing_point.city_direct_group = group
                        count += 1
                        if not node.start_point:
                            duration = node.rounded_arrival - start_time
                            if node.timing_point.city_time is None or node.timing_point.city_time > duration:
                                node.timing_point.city_time = duration
                                node.timing_point.city_quickest_group = group
          
