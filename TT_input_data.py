from TT_translators_data import RouteCodeTranslator, TimingPointTranslator, EdgeTranslator, LineOfRouteTranslator, TrainTypeTranslator

class RouteCodeInputter(object):

    def __init__(self, route_code_controller):
        self.route_code_controller = route_code_controller
        
    def create_route_code(self):
        route_code_translator = RouteCodeTranslator()
        route_code_string = raw_input('Please give the name of the route code. ')
        maximum_speed_string = raw_input('Please give the line speed of the route code. ')
        colour = raw_input('Please give the colour that should represent this route code on graphs, such as #7f0000 for red. ')
        route_code_line = ';'.join([route_code_string, maximum_speed_string, colour])
        route_code = route_code_translator.decode(route_code_line)
        self.route_code_controller[route_code_string] = route_code
                
    def delete_route_code(self):
        route_code_string = raw_input('Please give the name of the route code that you want to delete. ')
        confirm = raw_input('Please hit "y" if you sure that you want to delete %s. Otherwise, hit another key. ' % (route_code_string))
        if confirm == 'y':
            self.route_code_controller.delete(route_code_string)

    def input_route_code(self):
        choice = raw_input('Hit "c" to create a route code, or hit "d" to delete one. Hit "p" not to do anything. ')
        if choice == "c":
            self.create_route_code()
        if choice == "d":
            self.delete_route_code()
        if choice == "p":
            pass

class TimingPointInputter(object):

    def __init__(self, route_code_controller, timing_point_controller):
        self.route_code_controller = route_code_controller
        self.timing_point_controller = timing_point_controller

    def create_timing_point(self):
        timing_point_translator = TimingPointTranslator(self.route_code_controller)
        name = raw_input('Please give the name of the timing point. ')
        abbrev = raw_input('Please give the abbreviation of the timing point name. ')
        timing_point_type = raw_input('Please give the timing point type: "s" for a station, "j" for a junction, "y" for a yard and "l" for a loop. ')
        default_halt_string = raw_input('Please hit "y" if this a default stopping location, and "n" otherwise. ')
        if default_halt_string == 'y':
            default_halt_string = True
        if default_halt_string == 'n':
            default_halt_string = False
        default_dwell_string = raw_input('Please give the default dwell of the timing point. ')
        platform_routes_string = raw_input('Please give any necessary route codes pertaining to particular platforms, in the form "1:GL, 2:SL, 7:FL". If none are needed, then just hit Return. ')
        timing_point_line = ';'.join([name, abbrev, timing_point_type, default_halt_string, default_dwell_string, platform_routes_string])
        timing_point = timing_point_translator.decode(timing_point_line)
        self.timing_point_controller[name] = timing_point
        
    def delete_timing_point(self):
        name = raw_input('Please give the name of the timing point that you want to delete. ')
        confirm = raw_input('Please hit "y" if you sure that you want to delete %s. Otherwise, hit another key. ' % (name))
        if confirm == 'y':
            self.timing_point_controller.delete(name)
        
    def input_timing_point(self):
        choice = raw_input('Hit "c" to create a timing point, or hit "d" to delete one. Hit "p" not to do anything. ')
        if choice == "c":
            self.create_timing_point()
        if choice == "d":
            self.delete_timing_point()
        if choice == "p":
            pass

class EdgeInputter(object):
    
    def __init__(self, route_code_controller, timing_point_controller, edge_controller):
        self.route_code_controller = route_code_controller
        self.timing_point_controller = timing_point_controller
        self.edge_controller = edge_controller
        
    def create_edge(self):
        edge_translator = EdgeTranslator(self.timing_point_controller, self.route_code_controller)
        from_name = raw_input('Please give the name of the start timing point. ')
        to_name = raw_input('Please give the name of the end timing point. ')
        timing_point_from = self.timing_point_controller[from_name]
        timing_point_to = self.timing_point_controller[to_name]
        distance_string = raw_input('Please give the distance in miles between the two timing points. ')
        route_speeds_line = raw_input('Please give any exceptional line speeds pertaining to particular route codes, in the form "FL:80, SL:70, GL:20". If none are needed, then just hit Return. ')
        edge_line = ';'.join([from_name, to_name, distance_string, route_speeds_line])
        edge, back_edge = self.edge_translator.decode(edge_line)
        self.edge_controller[(edge.timing_point_from, edge.timing_point_to)] = edge
        self.edge_controller[(edge.timing_point_to, edge.timing_point_from)] = back_edge

    def delete_edge(self):
        to_name = raw_input('Please give the name of the start timing point. ')
        from_name = raw_input('Please give the name of the end timing point. ')
        timing_point_from = self.timing_point_controller[from_name]
        timing_point_to = self.timing_point_controller[to_name]
        edge = self.edge_controller[(timing_point_from, timing_point_to)]
        confirm = raw_input('Please hit "y" if you sure that you want to delete %s. Otherwise, hit another key. ' % (edge.name))
        if confirm == 'y':
            self.edge_controller.delete((timing_point_from, timing_point_to))
            self.edge_controller.delete((timing_point_to, timing_point_from))
        
    def input_edge(self):
        choice = raw_input('Hit "c" to create an edge, or hit "d" to delete one. Hit "p" not to do anything. ')
        if choice == "c":
            self.create_edge()
        if choice == "d":
            self.delete_edge()
        if choice == "p":
            pass        
    
class LineOfRouteInputter(object):

    def __init__(self, timing_point_controller, line_of_route_controller):
        self.timing_point_controller = timing_point_controller
        self.line_of_route_controller = line_of_route_controller
        
    def create_line_of_route(self):
        line_of_route_translator = LineOfRouteTranslator(self.timing_point_controller)
        line_of_route_line = raw_input('Please enter the timing points that form the line of route, separated by semicolons. If a timing point is to be optional, then add an asterisk after it. ')
        line_of_route = line_of_route_translator.decode(line_of_route_line)
        self.line_of_route_controller.add_item(line_of_route)
        
    def delete_line_of_route(self):
        line_of_route_number_string = raw_input('Please give the number of the line of route that you want to delete. ')
        line_of_route_number = int(line_of_route_number_string)
        line_of_route = self.line_of_route_controller[line_of_route_number]
        confirm = raw_input('Please hit "y" if you sure that you want to delete %s. Otherwise, hit another key. ' % (line_of_route.name))
        if confirm == 'y':
            self.line_of_route_controller.delete_item(line_of_route_number)
        
    def input_line_of_route(self):
        choice = raw_input('Hit "c" to create a line of route, or hit "d" to delete one. Hit "p" not to do anything. ')
        if choice == "c":
            self.create_line_of_route()
        if choice == "d":
            self.delete_line_of_route()
        if choice == "p":
            pass        

class TrainTypeInputter(object):

    def __init__(self, train_type_controller):
        self.train_type_controller = train_type_controller
        
    def create_train_type(self):
        train_type_translator = TrainTypeTranslator()
        name = raw_input('Please give the name of the train type. ')
        headcode_initial = raw_input('Please give the headcode initial number of this train type. ')
        maximum_speed_string = raw_input('Please give the maximum speed of this train type, in miles per hour. ')
        acceleration_string = raw_input('Please give the acceleration of this train type, in miles per hour per second. ')
        deceleration_string = raw_input('Please give the deceleration of this train type, in miles per hour per second. ')
        default_train_dwell_string = raw_input('Please give the default dwell time for this train type. ')
        train_type_line = ';'.join([name, headcode_initial, maximum_speed_string, acceleration_string, deceleration_string, default_train_dwell_string])
        train_type = train_type_translator.decode(train_type_line)
        self.train_type_controller[name] = train_type
        
    def delete_train_type(self):
        name = raw_input('Please give the name of the train type that you want to delete. ')
        confirm = raw_input('Please hit "y" if you sure that you want to delete %s. Otherwise, hit another key. ' % (name))
        if confirm == 'y':
            self.train_type_controller.delete(name)

    def input_train_type(self):
        choice = raw_input('Hit "c" to create a train type, or hit "d" to delete one. Hit "p" not to do anything. ')
        if choice == "c":
            self.create_train_type()
        if choice == "d":
            self.delete_train_type()
        if choice == "p":
            pass

class DataInputter(object):
    
    def __init__(self, data_controllers):
        self.data_controllers = data_controllers

    def input_data(self, choice):
        if choice == 'r':
            route_code_inputter = RouteCodeInputter(self.data_controllers.route_code_controller)
            route_code_inputter.input_route_code()
        if choice == 't':
            timing_point_inputter = TimingPointInputter(self.data_controllers.route_code_controller, self.data_controllers.timing_point_controller)
            timing_point_inputter.input_timing_point()
        if choice == 'e':
            edge_inputter = EdgeInputter(self.data_controllers.route_code_controller, self.data_controllers.timing_point_controller, self.data_controllers.edge_controller)
            edge_inputter.input_edge()
        if choice == 'l':
            line_of_route_inputter = LineOfRouteInputter(self.data_controllers.timing_point_controller, self.data_controllers.line_of_route_controller)
            line_of_route_inputter.input_line_of_route()
        if choice == 'y':
            train_type_inputter = TrainTypeInputter(self.data_controllers.train_type_controller)
            train_type_inputter.input_train_type()
