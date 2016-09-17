class DataChecker(object):

    def __init__(self, data_controllers, group_controller):
        self.data_controllers = data_controllers
        self.route_code_controller = self.data_controllers.route_code_controller
        self.timing_point_controller = self.data_controllers.timing_point_controller
        self.edge_controller = self.data_controllers.edge_controller
        self.line_of_route_controller = self.data_controllers.line_of_route_controller
        self.train_type_controller = self.data_controllers.train_type_controller
        self.group_controller = group_controller
        
    def check_timing_point_abbreviations(self):
        for timing_point_1 in self.timing_point_controller:
            for timing_point_2 in self.timing_point_controller:
                if timing_point_1 != timing_point_2:
                    if timing_point_1.abbrev == timing_point_2.abbrev:
                        print '%s and %s both have the abbreviation %s.' % (timing_point_1.name, timing_point_2.name, timing_point_1.abbrev)

    def check_unused_timing_points(self):
        self.unused_timing_points = set([])
        for timing_point in self.timing_point_controller:
            include = True
            for group in self.group_controller:
                for node in group.nodes:
                    if node.timing_point == timing_point:
                        include = False
            for line_of_route in self.line_of_route_controller:
                for node in line_of_route:
                    if node.timing_point == timing_point:
                        include = False
            if include == True:
                self.unused_timing_points.add(timing_point)
        if len(self.unused_timing_points) != 0:
            print 'The following %s timing points have not been used.' % (len(self.unused_timing_points))
            for timing_point in self.unused_timing_points:
                print timing_point.name

    def check_unused_edges(self):
        unused_single_edges = set()
        for edge in self.edge_controller:
            include = True
            for group in self.group_controller:
                if include == True:
                    for link in group.links:
                        if link.edge == edge:
                            include = False
   #         for line_of_route in self.line_of_route_controller:
    #            line_of_route.collect_seq_edges(self.edge_controller)
     #           if edge in line_of_route.seq_edges:
      #              include = False
            if include == True:
                if edge.timing_point_to not in self.unused_timing_points:
                    if edge.timing_point_from not in self.unused_timing_points:
                        unused_single_edges.add(edge)

        unused_edges = set()
        for edge_1 in unused_single_edges:
            for edge_2 in unused_single_edges:
                if edge_1.timing_point_from == edge_2.timing_point_to:
                    if edge_1.timing_point_to == edge_2.timing_point_from:
                        unused_edges.add(edge_1)
                        unused_edges.add(edge_2)

        if len(unused_edges) != 0:                    
            print 'The following %s edges have not been used.' % (len(unused_edges))
            for edge in unused_edges:
                print edge.name
            
    def check_missing_platform_route_codes(self):
        for group in self.group_controller:
            group.calculate_halts()
            for node in group.nodes:
                if node.halt and not node.end_point:
                    if node.previous_link.route_code != node.next_link.route_code:
                        if node.timing_point.platform_routes[node.platform] != node.previous_link.route_code:
                            if node.timing_point.platform_routes[node.platform] != node.next_link.route_code:
                                print '%s at %s transfers from %s to %s on platform %s, which has a default node of %s.' % (group.short_headcode.short_headcode_string, node.timing_point.name, node.previous_link.route_code.name, node.next_link.route_code.name, node.platform, node.timing_point.platform_routes[node.platform].name)
                                
    def check_route_code_colour_clashes(self):
        for line_of_route in self.line_of_route_controller:
            line_of_route.collect_seq_edges(self.edge_controller)
            line_of_route.collect_all_edges(self.edge_controller)
            used_route_codes = set()
            for group in self.group_controller:
                for link in group.links:
                    if link.edge in line_of_route.all_edges:
                        used_route_codes.add(link.route_code)
                    
            for route_code_1 in used_route_codes:
                for route_code_2 in used_route_codes:
                    if route_code_1.name < route_code_2.name:
                        if route_code_1.colour == route_code_2.colour:
                            print '%s and %s share the same colour, but are both used on %s.' % (route_code_1.name, route_code_2.name, line_of_route.name)
                            
    def check_headcodes(self):
        foul_headcodes = set()
        for group in self.group_controller:
            short_headcode = group.short_headcode
            if not short_headcode.is_valid():
                foul_headcodes.add(short_headcode.short_headcode_string)
        if len(foul_headcodes) != 0:
            print 'The following short headcodes are invalid.'
            for foul_headcode in foul_headcodes:
                print foul_headcode.short_headcode_string
                            
    def check_data(self):
        print 'Checking for duplicated timing point abbreviations.'
        self.check_timing_point_abbreviations()
        print 'Checking for missing platform route codes.'
        self.check_missing_platform_route_codes()
        print 'Checking for route code colour clashes.'
        self.check_route_code_colour_clashes()
        print 'Checking for unused timing points.'
        self.check_unused_timing_points()
        print 'Checking for unused edges.'
        self.check_unused_edges()
        print 'Checking for invalid headcodes.'
        self.check_headcodes()
