from csv import reader
from TT_basics_tools import Lister, Finder
from TT_translators_data import RouteCodeTranslator, TimingPointTranslator, EdgeTranslator, LineOfRouteTranslator, TrainTypeTranslator, SceneTranslator

# We create controllers to store data input in a helpful way.


class RouteCodeController(Finder):
    def __init__(self):
        Finder.__init__(self)
        self.route_code_names = set()


class TimingPointController(Finder):
    pass


class EdgeController(Finder):
    pass


class LineOfRouteController(Finder):
    pass


class TrainTypeController(Finder):
    pass


class SceneController(Finder):
    pass


# We create a tool to load a file of route codes and their attributes.

class RouteCodeLoader(object):
    def __init__(self):
        self.route_code_translator = RouteCodeTranslator()

    def do_import(self, route_code_filename):
        route_code_controller = RouteCodeController()
        with open(route_code_filename) as route_code_file:
            route_code_reader = reader(route_code_file, delimiter='|') # Don't want a delimiter really, so the line sign is just there for the beer.
            for route_code_line in route_code_reader:
                route_code = self.route_code_translator.decode(route_code_line[0])
                name = route_code.name
                route_code_controller[name] = route_code
                route_code_controller.route_code_names.add(name)
        return route_code_controller

    def do_export(self, route_code_controller, route_code_filename):
        route_code_file = open(route_code_filename, 'w')
        for route_code in route_code_controller:
            route_code_line = self.route_code_translator.encode(route_code)
            route_code_file.write(route_code_line)
            route_code_file.write('\n')
        route_code_file.close()


# We create a tool to load a file of timing points and their attributes.

class TimingPointLoader(object):
    def __init__(self, route_code_controller):
        self.route_code_controller = route_code_controller
        self.timing_point_translator = TimingPointTranslator(self.route_code_controller)

    def do_import(self, timing_point_filename):
        timing_point_controller = TimingPointController()
        with open(timing_point_filename) as timing_point_file:
            timing_point_reader = reader(timing_point_file, delimiter='|')
            for timing_point_line in timing_point_reader:
                timing_point = self.timing_point_translator.decode(timing_point_line[0])
                timing_point_controller[timing_point.name] = timing_point
        return timing_point_controller

    def do_export(self, timing_point_controller, timing_point_filename):
        timing_point_file = open(timing_point_filename, 'w')
        for timing_point in timing_point_controller:
            timing_point_line = self.timing_point_translator.encode(timing_point)
            timing_point_file.write(timing_point_line)
            timing_point_file.write('\n')
        timing_point_file.close()


# We create a tool to load a file of edges and their distances.

class EdgeLoader(object):
    def __init__(self, route_code_controller, timing_point_controller):
        self.route_code_controller = route_code_controller
        self.timing_point_controller = timing_point_controller
        self.edge_translator = EdgeTranslator(self.route_code_controller, self.timing_point_controller)

    def do_import(self, edge_filename):
        edge_controller = EdgeController()
        with open(edge_filename) as edge_file:
            edge_reader = reader(edge_file, delimiter='|')
            for edge_line in edge_reader:
                edge, back_edge = self.edge_translator.decode(edge_line[0])
                edge_controller[(edge.timing_point_from, edge.timing_point_to)] = edge
                edge_controller[(edge.timing_point_to, edge.timing_point_from)] = back_edge
        return edge_controller

    def do_export(self, edge_controller, edge_filename):
        edge_file = open(edge_filename, 'w')
        for edge in edge_controller:
            tp_from = edge.timing_point_from
            tp_to = edge.timing_point_to
            if tp_from.name < tp_to.name:
                edge_line = self.edge_translator.encode(edge)
                edge_file.write(edge_line)
                edge_file.write('\n')
        edge_file.close()


# We create a tool to load a file of lines of route.

class LineOfRouteLoader(object):
    def __init__(self, timing_point_controller):
        self.timing_point_controller = timing_point_controller
        self.line_of_route_translator = LineOfRouteTranslator(self.timing_point_controller)

    def do_import(self, line_of_route_filename):
        line_of_route_controller = LineOfRouteController()
        with open(line_of_route_filename) as line_of_route_file:
            line_of_route_reader = reader(line_of_route_file, delimiter='|')
            line_of_route_number = 0
            for line_of_route_line in line_of_route_reader:
                line_of_route = self.line_of_route_translator.decode(line_of_route_line[0])
                line_of_route_controller[line_of_route_number] = line_of_route
                line_of_route.number = line_of_route_number
                line_of_route_number = line_of_route_number + 1
        return line_of_route_controller

    def do_export(self, line_of_route_controller, line_of_route_filename):
        line_of_route_file = open(line_of_route_filename, 'w')
        for line_of_route in line_of_route_controller:
            line_of_route_line = self.line_of_route_translator.encode(line_of_route)
            line_of_route_file.write(line_of_route_line)
            line_of_route_file.write('\n')
        line_of_route_file.close()


# We create a tool to load a file of train types and their attributes.

class TrainTypeLoader(object):
    def __init__(self):
        self.train_type_translator = TrainTypeTranslator()

    def do_import(self, train_type_filename):
        train_type_controller = TrainTypeController()
        with open(train_type_filename) as train_type_file:
            train_type_reader = reader(train_type_file, delimiter='|')
            for train_type_line in train_type_reader:
                train_type = self.train_type_translator.decode(train_type_line[0])
                train_type_controller[train_type.name] = train_type
        return train_type_controller

    def do_export(self, train_type_controller, train_type_filename):
        train_type_file = open(train_type_filename, 'w')
        for train_type in train_type_controller:
            train_type_line = self.train_type_translator.encode(train_type)
            train_type_file.write(train_type_line)
            train_type_file.write('\n')
        train_type_file.close()


# We create a tool to load a file of visualisation scenes.

class SceneLoader(object):
    def __init__(self, timing_point_controller, edge_controller, route_code_controller):
        self.timing_point_controller = timing_point_controller
        self.edge_controller = edge_controller
        self.route_code_controller = route_code_controller
        self.scene_translator = SceneTranslator(self.timing_point_controller, self.edge_controller, self.route_code_controller)

    def do_import(self, scene_filename):
        scene_controller = SceneController()
        with open(scene_filename) as scene_file:
            scene_reader = reader(scene_file, delimiter='|')
            scene_number = 0
            for scene_line in scene_reader:
                if len(scene_line) != 0:
                    scene = self.scene_translator.decode(scene_line[0])
                    scene_controller[scene_number] = scene
                    scene.number = scene_number
                    scene_number = scene_number + 1
        return scene_controller


# Now we can import and export the data.

class DataControllers(object):
    def __init__(self, route_code_controller, timing_point_controller, edge_controller, line_of_route_controller, train_type_controller, scene_controller):
        self.route_code_controller = route_code_controller
        self.timing_point_controller = timing_point_controller
        self.edge_controller = edge_controller
        self.line_of_route_controller = line_of_route_controller
        self.train_type_controller = train_type_controller
        self.scene_controller = scene_controller


class DataLoader(object):
    def import_data(self, data_filenames_in):
        route_code_filename, timing_point_filename, edge_filename, line_of_route_filename, train_type_filename, scene_filename = data_filenames_in

        route_code_loader = RouteCodeLoader()
        route_code_controller = route_code_loader.do_import(route_code_filename)
        timing_point_loader = TimingPointLoader(route_code_controller)
        timing_point_controller = timing_point_loader.do_import(timing_point_filename)
        edge_loader = EdgeLoader(route_code_controller, timing_point_controller)
        edge_controller = edge_loader.do_import(edge_filename)
        line_of_route_loader = LineOfRouteLoader(timing_point_controller)
        line_of_route_controller = line_of_route_loader.do_import(line_of_route_filename)
        train_type_loader = TrainTypeLoader()
        train_type_controller = train_type_loader.do_import(train_type_filename)
        scene_loader = SceneLoader(timing_point_controller, edge_controller, route_code_controller)
        scene_controller = scene_loader.do_import(scene_filename)

        data_controllers = DataControllers(route_code_controller, timing_point_controller, edge_controller, line_of_route_controller, train_type_controller, scene_controller)

        return data_controllers

    def export_data(self, data_controllers, data_filenames_out):
        route_code_filename, timing_point_filename, edge_filename, line_of_route_filename, train_type_filename = data_filenames_out
        route_code_loader = RouteCodeLoader()
        route_code_loader.do_export(data_controllers.route_code_controller, route_code_filename)
        timing_point_loader = TimingPointLoader(data_controllers.route_code_controller)
        timing_point_loader.do_export(data_controllers.timing_point_controller, timing_point_filename)
        edge_loader = EdgeLoader(data_controllers.timing_point_controller, data_controllers.route_code_controller)
        edge_loader.do_export(data_controllers.edge_controller, edge_filename)
        line_of_route_loader = LineOfRouteLoader(data_controllers.timing_point_controller)
        line_of_route_loader.do_export(data_controllers.line_of_route_controller, line_of_route_filename)
        train_type_loader = TrainTypeLoader()
        train_type_loader.do_export(data_controllers.train_type_controller, train_type_filename)
