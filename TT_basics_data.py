from re import match
from TT_basics_tools import Finder, Lister

# We introduce route codes, which indicate which line a train will use between two timing points.

class RouteCode(object):

    def __init__(self, name, maximum_speed, colour):
        self.name = name
        self.maximum_speed = maximum_speed
        self.colour = colour

# We introduce timing points.

class TimingPoint(object):

    def __init__(self, name, abbrev, default_halt, default_dwell, platform_routes):
        self.name = name
        self.abbrev = abbrev
        self.default_dwell = default_dwell
        self.default_halt = default_halt
        self.platform_routes = platform_routes
        self.number_of_platforms = 1
        self.edges_in = []
        self.edges_out = []
    
    def add_edge_in(self, edge):
        self.edges_in.append(edge)
    
    def add_edge_out(self, edge):
        self.edges_out.append(edge)

class Station(TimingPoint):
    
    def __init__(self, name, abbrev, default_halt, default_dwell, platform_routes):
        TimingPoint.__init__(self, name, abbrev, default_halt, default_dwell, platform_routes)
        self.type = 's'
        
class Junction(TimingPoint):

    def __init__(self, name, abbrev, default_halt, default_dwell, platform_routes):
        TimingPoint.__init__(self, name, abbrev, default_halt, default_dwell, platform_routes)
        self.type = 'j'
        
class Loop(TimingPoint):

    def __init__(self, name, abbrev, default_halt, default_dwell, platform_routes):
        TimingPoint.__init__(self, name, abbrev, default_halt, default_dwell, platform_routes)
        self.type = 'l'
        
class Yard(TimingPoint):

    def __init__(self, name, abbrev, default_halt, default_dwell, platform_routes):
        TimingPoint.__init__(self, name, abbrev, default_halt, default_dwell, platform_routes)
        self.type = 'y'

class Siding(TimingPoint):

    def __init__(self, name, abbrev, default_halt, default_dwell, platform_routes):
        TimingPoint.__init__(self, name, abbrev, default_halt, default_dwell, platform_routes)
        self.type = 'i'

# We introduce platform route finders. These give the route code of certain platforms at certain timing points.

class PlatformRoutes(Finder):

    def __init__(self):
        Finder.__init__(self)
        
    def __getitem__(self, platform):
        if platform in self.finder:
            return self.finder[platform]
        
    def __iter__(self):
        return self.finder.iterkeys()
        
# We introduce edges, which connect timing points.

class Edge(object):

    def __init__(self, timing_point_from, timing_point_to, edge_length, route_speeds):
        self.timing_point_from = timing_point_from
        self.timing_point_to = timing_point_to
        self.edge_length = edge_length
        self.route_speeds = route_speeds
    
    @property
    def name(self):
        return '%s -> %s' % (self.timing_point_from.name, self.timing_point_to.name)

    def calculate_speed_limit(self, route_code):
        speed_limit = self.route_speeds[route_code]
        if speed_limit:
            return speed_limit
        return route_code.maximum_speed

# We introduce route speed finders. These give the speed of certain route codes on certain edges.

class RouteSpeeds(Finder):

    def __init__(self):
        Finder.__init__(self)
        
    def __getitem__(self, route_code):
        if route_code in self.finder:
            return self.finder[route_code]

    def __iter__(self):
        return self.finder.iterkeys()
                
# We introduce lines of route, which show which timing points are found in what sequence on a particular stretch of line. These will form the geography for timetable graphs.

class LineOfRouteNode(object):

    def __init__(self, timing_point, is_it_mandatory):
        self.timing_point = timing_point
        self.is_it_mandatory = is_it_mandatory

class LineOfRoute(Lister):

    def __init__(self):
        Lister.__init__(self)
    
    @property
    def first_location(self):
        return self[0].timing_point
        
    @property
    def last_location(self):
        return self[-1].timing_point
        
    @property
    def name(self):
        return '%s -> %s' % (self.first_location.name, self.last_location.name)
    
    def make_node_finder(self):
        self.node_finder = {}
        for node in self:
            self.node_finder[node.timing_point] = node
    
    def collect_seq_edges(self, edge_controller):
        self.seq_edges = Lister()
        self[0].distance_from_start = 0
        previous_node = None
        for node in self:
            if previous_node != None:
                edge = edge_controller[(previous_node.timing_point, node.timing_point)]
                self.seq_edges.add_item(edge)
                node.distance_from_start = previous_node.distance_from_start + edge.edge_length
            previous_node = node
        self.total_distance = self[-1].distance_from_start
        
    def collect_all_edges(self, edge_controller):
        self.all_edges = set()
        self.forward_edges = set()
        self.backward_edges = set()
        for index in range(self.length - 1):
            go_further = True
            step = 0
            while go_further:
                step = step + 1
                edge = edge_controller[(self[index].timing_point, self[index + step].timing_point)]
                reversed_edge = edge_controller[(self[index + step].timing_point, self[index].timing_point)]
                if edge != None:
                    self.forward_edges.add(edge)
                    self.all_edges.add(edge)
                    self.backward_edges.add(reversed_edge)
                    self.all_edges.add(reversed_edge)
                if self[index + step].is_it_mandatory:
                    go_further = False
                    
# We introduce different types of trains.

class TrainType(object):

    def __init__(self, name, headcode_initial, top_speed, acceleration, deceleration, default_train_dwell):
        self.name = name
        self.headcode_initial = headcode_initial
        self.top_speed = top_speed
        self.acceleration = acceleration
        self.deceleration = deceleration
        self.default_train_dwell = default_train_dwell
        self.passenger = False
        self.express = False
        if self.headcode_initial in set(['1', '2', '3']):
            self.passenger = True
        if self.headcode_initial == '1':
            self.express = True
        
# We introduce short headcodes - four-character strings that identify train groups.

class ShortHeadcode(object):

    def __init__(self, short_headcode_string):
        self.short_headcode_string = short_headcode_string
    
    def is_valid(self):
        if len(self.short_headcode_string) != 4:
            return False
        if match('\d[A-Z](\d\d|[A-Z][A-Z])', self.short_headcode_string) is None:
            return False
        return True
        
# We introduce headcodes - six-character strings that identify individual trains.
        
class Headcode(object):

    def __init__(self, headcode_string, short_headcode):
        self.headcode_string = headcode_string
        self.short_headcode = short_headcode

# Schedule notes will be collected in a list.

class Notes(Lister):
    
    def __init__(self):
        Lister.__init__(self)

# Scene nodes and links will be used for timetable visualisations.

class SceneNode(object):

    def __init__(self, timing_point, platform_locations, platforms, dot_locations):
        self.timing_point = timing_point
        self.platform_locations = platform_locations
        self.platforms = platforms
        self.dot_locations = dot_locations

class SceneLink(object):

    def __init__(self, begin_scene_node, end_scene_node, route_locations, routes):
        self.begin_scene_node = begin_scene_node
        self.end_scene_node = end_scene_node
        self.route_locations = route_locations
        self.routes = routes

class Scene(object):

    def __init__(self):
        self.scene_nodes = []
        self.scene_links = []
        self.main_scene_links = []

    def add_node(self, scene_node):
        self.scene_nodes.append(scene_node)
    
    def add_link(self, scene_link):
        self.scene_links.append(scene_link)
    
    def add_main_link(self, scene_link):
        self.main_scene_links.append(scene_link)

    def assign_x(self):
        minimum_x, maximum_x = 0, 0
        number_of_scene_nodes_left = len(self.scene_nodes) - 1 # because the pivot station already has x = 0
        while number_of_scene_nodes_left > 0:
            for scene_link in self.main_scene_links:
                if scene_link.begin_scene_node.x == None and scene_link.end_scene_node.x != None:
                    scene_link.begin_scene_node.x = scene_link.end_scene_node.x - scene_link.length
                    number_of_scene_nodes_left = number_of_scene_nodes_left - 1
                    if scene_link.begin_scene_node.x < minimum_x:
                        minimum_x = scene_link.begin_scene_node.x
                if scene_link.begin_scene_node.x != None and scene_link.end_scene_node.x == None:
                    scene_link.end_scene_node.x = scene_link.begin_scene_node.x + scene_link.length
                    number_of_scene_nodes_left = number_of_scene_nodes_left - 1
                    if scene_link.end_scene_node.x > maximum_x:
                        maximum_x = scene_link.end_scene_node.x
        self.minimum_x, self.maximum_x = minimum_x, maximum_x
        self.total_distance = maximum_x - minimum_x   

    def assign_locations(self):
        for scene_node in self.scene_nodes:
            scene_node.location = (scene_node.x - self.minimum_x, scene_node.y)

        for scene_link in self.scene_links:
            scene_link.begin_location = scene_link.begin_scene_node.location
            scene_link.end_location = scene_link.end_scene_node.location

    def find_groups(self, group_controller):
        self.scene_groups = []
        for group in group_controller:
            for scene_link in self.scene_links:
                if group.is_at(scene_link.begin_scene_node.timing_point):
                    if group.is_at(scene_link.begin_scene_node.timing_point):
                        self.scene_groups.append(group)
                        break

    def set_up_scene(self, group_controller):
        self.assign_x()
        self.assign_locations()
        self.find_groups(group_controller)
