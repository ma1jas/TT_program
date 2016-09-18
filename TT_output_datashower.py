from TT_translators_data import LineOfRouteTranslator

class RouteCodeShower(object):

    def __init__(self, route_code_controller, edge_controller):
        self.route_code_controller = route_code_controller
        self.edge_controller = edge_controller

    def show_route_code_data(self):
        choice = raw_input('Please give the route code that you want information about. If you want a list of all route codes and their information, then just hit Return. ')
        if choice != '':
            route_code = self.route_code_controller[choice]
            print '\nRoute code %s has line speed %smph, and is represented by colour %s on graphs.\n' % (route_code.name, 60*route_code.maximum_speed, route_code.colour)
            for edge in self.edge_controller:
                if route_code in edge.route_speeds:
                    print 'On %s the line speed is %smph.' % (edge.name, 60*edge.route_speeds[route_code])
        else:
            for route_code in self.route_code_controller:
                print 'Route code %s has line speed %smph, and is represented by colour %s on graphs.' % (route_code.name, 60*route_code.maximum_speed, route_code.colour)

class TimingPointShower(object):

    def __init__(self, timing_point_controller, line_of_route_controller):
        self.timing_point_controller = timing_point_controller
        self.line_of_route_controller = line_of_route_controller

    def show_timing_point_data(self):
        name = raw_input('Please give the name of the timing point that you want information about. ')
        timing_point = self.timing_point_controller[name]
        timing_point_types = {'s': 'station', 'y': 'yard', 'l': 'loop', 'j': 'junction'}
        type_string = timing_point_types[timing_point.type]
        if timing_point.default_halt == True:
            stop = 'stopping'
        else:
            stop = 'passing'
        print '\n%s (%s) is a %s (a %s location), with a standard dwell of %s minutes.\n' % (name, timing_point.abbrev, type_string, stop, timing_point.default_dwell)
        index = 0
        for line_of_route in self.line_of_route_controller:
            for node in line_of_route:
                if node.timing_point == timing_point:
                    print '%s is found on line of route number %s (%s).' % (name, index, line_of_route.name)
            index = index + 1
        for platform in timing_point.platform_routes:
            route_code = timing_point.platform_routes[platform]
            print 'Platform %s lies on %s.' % (platform, route_code.name)

class EdgeShower(object):

    def __init__(self, timing_point_controller, edge_controller):
        self.timing_point_controller = timing_point_controller
        self.edge_controller = edge_controller

    def show_edge_data(self):
        from_string = raw_input('Please give the name of the start timing point. ')
        to_string = raw_input('Please give the name of the end timing point. ')
        timing_point_from = self.timing_point_controller[from_string]
        timing_point_to = self.timing_point_controller[to_string]
        edge = self.edge_controller[(timing_point_from, timing_point_to)]
        print '%s is %s miles long.' % (edge.name, edge.edge_length)
        for route_code in edge.route_speeds:
            speed = edge.route_speeds[route_code]
            print 'On this edge, %s has maximum speed %smph.' % (route_code.name, 60*speed)

class LineOfRouteShower(object):

    def __init__(self, timing_point_controller, line_of_route_controller):
        self.timing_point_controller = timing_point_controller
        self.line_of_route_controller = line_of_route_controller

    def show_line_of_route_data(self):
        choice = raw_input('Please give the line of route that you want information about. If you want a list of all lines of route, then just hit Return. ')
        if choice != '':
            line_of_route_number = int(choice)
            line_of_route = self.line_of_route_controller[line_of_route_number]
            line_of_route_translator = LineOfRouteTranslator(self.timing_point_controller)
            line_of_route_line = line_of_route_translator.encode(line_of_route)
            print line_of_route_line
        else:
            index = 0
            for line_of_route in self.line_of_route_controller:
                print '%s: %s (%s timing points)' % (index, line_of_route.name, line_of_route.length)
                index = index + 1

class TrainTypeShower(object):

    def __init__(self, train_type_controller):
        self.train_type_controller = train_type_controller

    def show_train_type_data(self):
        choice = raw_input('Please give the name of the train type that you want information about. ')
        train_type = self.train_type_controller[choice]
        print '%s trains have headcode initial %s and a standard dwell time of %s minutes. The top speed is %smph, the acceleration is %smph per second, and the deceleration is %smph per second.' % (train_type.name, train_type.headcode_initial, train_type.default_train_dwell, 60*train_type.top_speed, train_type.acceleration, train_type.deceleration)

class DataShower(object):

    def __init__(self, data_controllers):
        self.data_controllers = data_controllers

    def show_data(self):
        choice = raw_input('Hit "r" to show route code data.\nHit "t" to show timing point data.\nHit "e" to show edge data.\nHit "l" to show line of route data.\nHit "y" to show train type data.')

        if choice == 'r':
            route_code_shower = RouteCodeShower(self.data_controllers.route_code_controller, self.data_controllers.edge_controller)
            route_code_shower.show_route_code_data()
        if choice == 't':
            timing_point_shower = TimingPointShower(self.data_controllers.timing_point_controller, self.data_controllers.line_of_route_controller)
            timing_point_shower.show_timing_point_data()
        if choice == 'e':
            edge_shower = EdgeShower(self.data_controllers.timing_point_controller, self.data_controllers.edge_controller)
            edge_shower.show_edge_data()
        if choice == 'l':
            line_of_route_shower = LineOfRouteShower(self.data_controllers.timing_point_controller, self.data_controllers.line_of_route_controller)
            line_of_route_shower.show_line_of_route_data()
        if choice == 'y':
            train_type_shower = TrainTypeShower(self.train_type_controller)
            train_type_shower.show_train_type_data()
