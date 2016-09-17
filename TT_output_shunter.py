from TT_basics_data import Siding, Edge, PlatformRoutes, RouteSpeeds
from TT_translators_schedules import GroupTranslator, TimeTranslator, FrequencyTranslator

from datetime import datetime, timedelta

class Shunter(object):
    
    def __init__(self, data_controllers, group_controller):
        self.data_controllers = data_controllers
        self.timing_point_controller = self.data_controllers.timing_point_controller
        self.edge_controller = self.data_controllers.edge_controller
        self.group_controller = group_controller

    def create_infrastructure(self, terminus, siding_name):
        abbrev = ''.join(['I', terminus.abbrev[0:2]])
        platform_routes = PlatformRoutes()
        siding = Siding(siding_name, abbrev, True, 3, platform_routes)

        route_speeds = RouteSpeeds()
        forward_edge = Edge(terminus, siding, 0.125, route_speeds)
        backward_edge = Edge(siding, terminus, 0.125, route_speeds)
        self.timing_point_controller[siding_name] = siding
        self.edge_controller[(forward_edge.timing_point_from, forward_edge.timing_point_to)] = forward_edge
        self.edge_controller[(backward_edge.timing_point_from, backward_edge.timing_point_to)] = backward_edge
        return siding

    def make_shunt(self):
        passenger_short_headcode_string = raw_input('Please give the headcode of the train group. ')
        passenger_group = self.group_controller[passenger_short_headcode_string]
        terminus_node = passenger_group.nodes[0]
        terminus = terminus_node.timing_point
        siding_name = ''.join([terminus.name, ' Sidings'])
        siding = self.timing_point_controller[siding_name]
        if siding == None:
            siding = self.create_infrastructure(terminus, siding_name)
        short_headcode_string = ''.join(['5', passenger_short_headcode_string[1:4]])
        if self.group_controller[short_headcode_string] is not None:
            print 'There is already a group with headcode %s.' % (short_headcode_string)
        else:
            train_type_string = passenger_group.train_type.name
            notes_line = ''
            association_string = '3'
            time_translator = TimeTranslator()
            principle_start_time = passenger_group.principle_start_time - timedelta(minutes=8)
            if principle_start_time.hour != 0:
                principle_start_time += timedelta(minutes = passenger_group.frequency)
            principle_start_time_string = time_translator.encode(principle_start_time)
            frequency_translator = FrequencyTranslator()
            frequency_string = frequency_translator.encode(passenger_group.frequency)
            route_code = terminus_node.next_link.route_code
            platform = terminus_node.platform
            siding_track = route_code.name[0]
            journey_line = ''.join([terminus.name, ',', platform, ';', route_code.name, ';', siding.name, ',', siding_track, ',d3;', terminus.name, ',', platform])
            group_translator = GroupTranslator(self.data_controllers)
            group = group_translator.decode(short_headcode_string, train_type_string, notes_line, association_string, principle_start_time_string, frequency_string, journey_line)
            self.group_controller[short_headcode_string] = group
