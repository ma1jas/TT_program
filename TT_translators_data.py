from __future__ import division
from TT_basics_tools import split_strip, Finder, Lister
from TT_basics_data import RouteCode, PlatformRoutes, RouteSpeeds, Station, Yard, Loop, Junction, Siding, Edge, TrainType, LineOfRouteNode, LineOfRoute, SceneNode, SceneLink, Scene


# We create a tool that translates route code input and output.

class RouteCodeTranslator(object):
    def decode(self, route_code_line):
        name_string, maximum_speed_string, colour_string = split_strip(route_code_line, ';')
        maximum_speed = float(maximum_speed_string)/60
        route_code = RouteCode(name_string, maximum_speed, colour_string)
        return route_code
        
    def encode(self, route_code):
        name_string = route_code.name
        maximum_speed_string = str(60*route_code.maximum_speed)
        colour_string = route_code.colour
        route_code_line = ';'.join([name_string, maximum_speed_string, colour_string])
        return route_code_line


# We create a tool that translates platform route finder input and output.

class PlatformRouteTranslator(object):
    def __init__(self, route_code_controller):
        self.route_code_controller = route_code_controller
        
    def decode(self, platform_routes_line):
        platform_routes = PlatformRoutes()
        if platform_routes_line.strip() != '':
            platform_route_strings = platform_routes_line.split(',')
            for platform_route_string in platform_route_strings:
                platform_string, route_code_name = split_strip(platform_route_string, ':')
                route_code = self.route_code_controller[route_code_name]
                platform_routes[platform_string] = route_code
        return platform_routes
            
    def encode(self, platform_routes):
        platform_routes_line = ''
        if not platform_routes.is_it_empty():
            platform_route_strings = []
            for platform in platform_routes:
                route_code = platform_routes[platform]
                route_code_name = route_code.name
                platform_route_string = ':'.join([platform, route_code_name])
                platform_route_strings.append(platform_route_string)
            platform_routes_line = ','.join(platform_route_strings)
        return platform_routes_line


# We create a tool that translates timing point input and output.

class TimingPointTranslator(object):
    def __init__(self, route_code_controller):
        self.route_code_controller = route_code_controller
        self.platform_route_translator = PlatformRouteTranslator(self.route_code_controller)
        self.timing_point_types = {'s': Station, 'y': Yard, 'l': Loop, 'j': Junction, 'i': Siding}

    def decode(self, timing_point_line):
        name_string, abbrev_string, timing_point_type_string, default_halt_string, default_dwell_string, platform_routes_string = split_strip(timing_point_line, ';')
        default_halt = False
        if default_halt_string =='True':
            default_halt = True
        default_dwell = float(default_dwell_string)
        platform_routes = self.platform_route_translator.decode(platform_routes_string)
        timing_point_type = self.timing_point_types[timing_point_type_string]
        timing_point = timing_point_type(name_string, abbrev_string, default_halt, default_dwell, platform_routes)
        if abbrev_string[0] == 'Z':
            timing_point.city = True
        else:
            timing_point.city = False
        timing_point.city_time = None
        timing_point.city_direct_group = None
        timing_point.city_calls = None
        timing_point.city_quickest_group = None
        return timing_point
            
    def encode(self, timing_point):
        name_string = timing_point.name
        abbrev_string = timing_point.abbrev
        timing_point_type_string = timing_point.type
        default_halt_string = 'False'
        if timing_point.default_halt:
            default_halt_string = 'True'
        default_dwell_string = str(timing_point.default_dwell)
        platform_routes_string = self.platform_route_translator.encode(timing_point.platform_routes)
        timing_point_line = ';'.join([name_string, abbrev_string, timing_point_type_string, default_halt_string, default_dwell_string, platform_routes_string])
        return timing_point_line


# We create a tool that translates route speed input and output.

class RouteSpeedTranslator(object):
    def __init__(self, route_code_controller):
        self.route_code_controller = route_code_controller
        
    def decode(self, route_speeds_line):
        route_speeds = RouteSpeeds()
        if route_speeds_line.strip() != '':
            route_speed_strings = route_speeds_line.split(',')
            for route_speed_string in route_speed_strings:
                route_code_string, speed_string = split_strip(route_speed_string, ':')
                route_code = self.route_code_controller[route_code_string]
                speed = float(speed_string)/60
                route_speeds[route_code] = speed
        return route_speeds
        
    def encode(self, route_speeds):
        route_speeds_line = ''
        if not route_speeds.is_it_empty():
            route_speed_strings = []
            for route_code in route_speeds:
                route_code_string = route_code.name
                speed = route_speeds[route_code]
                speed_string = str(60*speed)
                route_speed_string = ':'.join([route_code_string, speed_string])
                route_speed_strings.append(route_speed_string)
            route_speeds_line = ','.join(route_speed_strings)
        return route_speeds_line
        

# We create a tool that translates edge input and output.

class EdgeTranslator(object):    
    def __init__(self, route_code_controller, timing_point_controller):
        self.route_code_controller = route_code_controller
        self.timing_point_controller = timing_point_controller
        self.route_speed_translator = RouteSpeedTranslator(self.route_code_controller)

    def decode(self, edge_line):
        timing_point_from_string, timing_point_to_string, distance_string, route_speeds_line = split_strip(edge_line, ';')
        timing_point_from = self.timing_point_controller[timing_point_from_string]
        timing_point_to = self.timing_point_controller[timing_point_to_string]
        edge_length = float(distance_string)
        route_speeds = self.route_speed_translator.decode(route_speeds_line)
        edge = Edge(timing_point_from, timing_point_to, edge_length, route_speeds)
        back_edge = Edge(timing_point_to, timing_point_from, edge_length, route_speeds)
        return edge, back_edge
        
    def encode(self, edge):
        timing_point_from_string = edge.timing_point_from.name
        timing_point_to_string = edge.timing_point_to.name
        distance_string = str(edge.edge_length)
        edge.route_speeds
        route_speeds_line = self.route_speed_translator.encode(edge.route_speeds)
        edge_line = ';'.join([timing_point_from_string, timing_point_to_string, distance_string, route_speeds_line])
        return edge_line
        

# We create a tool that translates line of route input and output.

class LineOfRouteTranslator(object):
    def __init__(self, timing_point_controller):
        self.timing_point_controller = timing_point_controller
    
    def decode(self, line_of_route_line):
        line_of_route = LineOfRoute()
        node_string_list = split_strip(line_of_route_line, ';')
        for node_string in node_string_list:
            timing_point_string = node_string.split('*')[0]
            timing_point_string = timing_point_string.strip()
            timing_point = self.timing_point_controller[timing_point_string]
            is_it_mandatory = True
            if '*' in node_string:
                is_it_mandatory = False
            line_of_route_node = LineOfRouteNode(timing_point, is_it_mandatory)
            line_of_route.add_item(line_of_route_node)
        return line_of_route

    def encode(self, line_of_route):
        line_of_route_node_strings = []
        for line_of_route_node in line_of_route:
            line_of_route_node_string = str(line_of_route_node.timing_point.name)
            if not line_of_route_node.is_it_mandatory:
                line_of_route_node_string = ''.join([line_of_route_node_string, '*'])
            line_of_route_node_strings.append(line_of_route_node_string)
        line_of_route_line = ';'.join(line_of_route_node_strings)
        return line_of_route_line


# We create a tool that translates train type input and output.
        
class TrainTypeTranslator(object):
    def decode(self, train_type_line):
        train_type_string, headcode_initial_string, top_speed_string, acceleration_string, deceleration_string, default_train_dwell_string = split_strip(train_type_line, ';')
        top_speed = float(top_speed_string)/60
        acceleration = float(acceleration_string)
        deceleration = float(deceleration_string)
        default_train_dwell = float(default_train_dwell_string)
        train_type = TrainType(train_type_string, headcode_initial_string, top_speed, acceleration, deceleration, default_train_dwell)
        return train_type
        
    def encode(self, train_type):
        train_type_string = train_type.name
        headcode_initial_string = train_type.headcode_initial
        top_speed_string = str(60*train_type.top_speed)
        acceleration_string = str(train_type.acceleration)
        deceleration_string = str(train_type.deceleration)
        default_train_dwell_string = str(train_type.default_train_dwell)
        train_type_line = ';'.join([train_type_string, headcode_initial_string, top_speed_string, acceleration_string, deceleration_string, default_train_dwell_string])
        return train_type_line


# We create a tool that translates visualisation scene input.

class SceneTranslator(object):
    def __init__(self, timing_point_controller, edge_controller, route_code_controller):
        self.timing_point_controller = timing_point_controller
        self.edge_controller = edge_controller
        self.route_code_controller = route_code_controller

    def decode_platform_string(self, platform_string):
        platform_locations = {}
        platforms = []
        dot_locations = []
        location = 1
        track_y_max = 1
        platform_inputs = self.split_strip(platform_string, ',')
        for platform_input in platform_inputs:
            platform_details = self.split_strip(platform_input, '@')
            show_platform_name = True
            platform = platform_details[0]
            if '*' in platform:
                show_platform_name = False
                platform = self.split_strip(platform, '*')[0]
            if platform != 'x':
                if len(platform_details) == 1:
                    platform_y = location
                else:
                    platform_y = float(platform_details[1])
                if platform == '.':
                    dot_locations.append(platform_y)
                else:
                    platform_locations[platform] = (platform_y, show_platform_name)
                    platforms.append(platform)
                if platform_y > track_y_max:
                    track_y_max = platform_y
            location = location + 1
        return platform_locations, platforms, dot_locations, track_y_max

    def decode_route_item(self, route_item, location):
        split_route_item = self.split_strip(route_item, '@')
        route_plus_direction_string = split_route_item[0]
        route_code_string, forward_string = route_plus_direction_string[:-1], route_plus_direction_string[-1]
        show_route_code = True
        if '^' in route_code_string:
            show_route_code = False
            route_code_string = self.split_strip(route_code_string, '^')[0]
        route_code = self.route_code_controller[route_code_string]
        if route_code == None:
            print route_item
        forwards = True
        if forward_string == 'b':
            forwards = False
        if len(split_route_item) == 1:
            return (route_code, forwards), ((location, location), show_route_code)
        elif len(split_route_item) == 2:
            return (route_code, forwards), ((float(split_route_item[1]), float(split_route_item[1])), show_route_code)
        elif len(split_route_item) == 3:
            return (route_code, forwards), ((float(split_route_item[1]), float(split_route_item[2])), show_route_code)
            
    def decode_route_string(self, route_string):
        route_locations = {}
        routes = []
        location = 1
        route_items = self.split_strip(route_string, ',')
        for route_item in route_items:
            (route_code, forwards), ((route_begin_y, route_end_y), show_route_code) = self.decode_route_item(route_item, location)
            route_locations[(route_code, forwards)] = ((route_begin_y, route_end_y), show_route_code)
            routes.append((route_code, forwards))
            location = location + 1
        return route_locations, routes

    def decode_node_information(self, node_information):
        timing_point_name, y_string, platform_string = self.split_strip(node_information, ':')
        timing_point = self.timing_point_controller[timing_point_name]
        platform_locations, platforms, dot_locations, track_y_max = self.decode_platform_string(platform_string)
        scene_node = SceneNode(timing_point, platform_locations, platforms, dot_locations)
        scene_node.x = None
        scene_node.y = int(y_string)
        scene_node.node_y_max = scene_node.y + track_y_max
        return scene_node

    def decode_link_information(self, link_information):
        if link_information == None:
            return []
        make_into_links = []
        link_inputs = self.split_strip(link_information, ':')
        for link_input in link_inputs:
            if '>' in link_input or '}' in link_input:
                link_from = link_input
                outwards = False
                main = True
                if '}' in link_from:
                    main = False
                where = int(link_from[1:])
                route_locations = None
                routes = None
            else:
                outwards = True
                main = True
                if '*' not in link_input:
                    route_string = link_input
                    where = 0
                else:
                    route_string, link_to = self.split_strip(link_input, '*')
                    if '{' in link_to:
                        main = False
                    where = int(link_to[1:])
                route_locations, routes = self.decode_route_string(route_string)
            make_into_links.append((outwards, main, where, route_locations, routes))
        return make_into_links

    def process_scene_link(self, scene_link):
        scene_link.edge = self.edge_controller[scene_link.begin_scene_node.timing_point, scene_link.end_scene_node.timing_point]
        if scene_link.edge == None:
            begin_name, end_name = scene_link.begin_scene_node.timing_point.name, scene_link.end_scene_node.timing_point.name
            print ''.join(['There is no edge between ', begin_name, ' and ', end_name, '.'])
        scene_link.reverse_edge =  self.edge_controller[scene_link.end_scene_node.timing_point, scene_link.begin_scene_node.timing_point]
        scene_link.length = scene_link.edge.edge_length

    def decode(self, scene_line):
        scene = Scene()
        scene.y_max = 2
        partial_scene_links = {}
        partial_scene_link_from_previous = None
        first_node = True
        scene_inputs = self.split_strip(scene_line, ';')
        for scene_input in scene_inputs:
            split_information = self.split_strip(scene_input, '#')
            node_information, link_information = split_information[0], None
            if len(split_information) == 2:
                link_information = split_information[1]
            scene_node = self.decode_node_information(node_information)
            if first_node:
                scene_node.x = 0
                first_node = False
            scene.add_node(scene_node)
            if scene_node.node_y_max > scene.y_max:
                scene.y_max = scene_node.node_y_max
            if partial_scene_link_from_previous != None:
                main, previous_scene_node, route_locations, routes = partial_scene_link_from_previous
                scene_link = SceneLink(previous_scene_node, scene_node, route_locations, routes)
                self.process_scene_link(scene_link)
                scene.add_link(scene_link)
                if main:
                    scene.add_main_link(scene_link)
            partial_scene_link_from_previous = None

            make_into_links = self.decode_link_information(link_information)
            for outwards, main, where, route_locations, routes in make_into_links:
                if outwards:
                    if where == 0:
                        partial_scene_link_from_previous = (main, scene_node, route_locations, routes)
                    else:
                        partial_scene_links[where] = (main, scene_node, route_locations, routes)
                else:
                    main, begin_scene_node, route_locations, routes = partial_scene_links[where]
                    scene_link = SceneLink(begin_scene_node, scene_node, route_locations, routes)
                    self.process_scene_link(scene_link)
                    scene.add_link(scene_link)
                    if main:
                        scene.add_main_link(scene_link)
        return scene
