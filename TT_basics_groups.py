from __future__ import division
from datetime import datetime, timedelta, time
from math import sqrt
from TT_basics_tools import Lister
from TT_basics_trains import HeadcodeConverter, Train
                
# We introduce a gadget that will compute SRTs within a schedule. Unfortunately this requires rather a lot of inelegant maths, although most of it is just v^2=u^2+2as and v=u+at stuff.

class SpeedProfile(object):

    def __init__(self, acc_time, dec_time, srt, acc_distance, dec_distance, distance, initial_speed, achieved_speed, final_speed):
        self.acc_time = acc_time
        self.dec_time = dec_time
        self.srt = srt
        self.acc_distance = acc_distance
        self.dec_distance = dec_distance
        self.distance = distance
        self.initial_speed = initial_speed
        self.achieved_speed = achieved_speed
        self.final_speed = final_speed

class SRTCalculator(object):

    def calculate_srt(self, initial_speed, final_speed, speed_limit, distance, acceleration, deceleration):

        bigger_speed = max(initial_speed, final_speed)
        harmonic = 2*acceleration*deceleration/(acceleration + deceleration)
        if final_speed >= initial_speed:
            matching_distance = (final_speed**2 - initial_speed**2)/(2*acceleration)
        else:
            matching_distance = (initial_speed**2 - final_speed**2)/(2*deceleration)
        achieved_speed = min(speed_limit, sqrt(bigger_speed**2 + harmonic*(distance - matching_distance)))

        acc_distance = (achieved_speed**2 - initial_speed**2)/(2*acceleration)
        dec_distance = (achieved_speed**2 - final_speed**2)/(2*deceleration)
        coasting_distance = distance - acc_distance - dec_distance
        acc_time = (achieved_speed - initial_speed)/acceleration
        dec_time = (achieved_speed - final_speed)/deceleration
        coasting_time = coasting_distance/achieved_speed
        srt = acc_time + coasting_time + dec_time

        speed_profile = SpeedProfile(acc_time, dec_time, srt, acc_distance, dec_distance, distance, initial_speed, achieved_speed, final_speed)
        return speed_profile

# We introduce schedule nodes and links - objects that reference each timing point and edge (respectively) in a schedule, along with some other values pertaining to that point or edge.

class JourneyItem(object):

    pass

class Node(JourneyItem):

    def __init__(self, timing_point, platform, halt_modifier, dwell_modifier, node_speed_limit):
        JourneyItem.__init__(self)
        self.timing_point = timing_point
        self.platform = platform
        try:
            platform_number = int(self.platform)
            self.timing_point.number_of_platforms = max(self.timing_point.number_of_platforms, platform_number)
        except:
            pass
        self.halt_modifier = halt_modifier
        self.dwell_modifier = dwell_modifier
        self.node_speed_limit = node_speed_limit
        
class LinkModifier(JourneyItem):

    def __init__(self, route_code, pathing):
        JourneyItem.__init__(self)
        self.route_code = route_code
        self.pathing = pathing
        
class Link(JourneyItem):

    def __init__(self, route_code, pathing):
        JourneyItem.__init__(self)
        self.route_code = route_code
        self.pathing = pathing

# Journey nodes and journey links will combine to make journey specifications.

class JourneySpec(Lister):

    def __init__(self):
        Lister.__init__(self)

# We can now introduce a train group.
        
class Group(object):

    def __init__(self, short_headcode, train_type, notes, association, principle_start_time, frequency, nodes, links):
        self.short_headcode = short_headcode
        self.train_type = train_type
        self.notes = notes
        self.association = association
        self.principle_start_time = principle_start_time
        self.frequency = frequency
        self.nodes = nodes
        self.links = links
        self.first_timing_point = self.nodes[0].timing_point
        self.last_timing_point = self.nodes[-1].timing_point
        self.city_starter = False
        if self.first_timing_point.city:
            self.city_starter = True
        self.city_finisher = False
        if self.last_timing_point.city:
            self.city_finisher = True
       
    def calculate_halts(self):
        for node in self.nodes:
            if node.halt_modifier != None:
                # The next three lines simply correct any redundant 'x's in non-passenger trains.
                if not self.train_type.passenger:
                    if not node.halt_modifier:
                        node.halt_modifier = None
                node.halt = node.halt_modifier
            # If there is no halt modifier at a station in a non-passenger train, then it is assumed to be a pass.
            elif node.timing_point.type == 's' and not self.train_type.passenger:
                node.halt = False
            # If there is no halt modifier in a passenger train, then it is assumed to be a stop.
            else:
                node.halt = node.timing_point.default_halt
        
        # We must force a stop at the first and last locations.
        self.nodes[0].halt = True
        self.nodes[-1].halt = True
        
        for node in self.nodes:
            if node.halt and not node.end_point:
                if node.route_code_changes:
                    node.route_code = node.timing_point.platform_routes[node.platform]
                else:
                    node.route_code = node.previous_link.route_code
            else:
                node.route_code = None
    
    def calculate_dwells(self):
        for node in self.nodes:
            if node.halt:
                if node.dwell_modifier != None:
                    node.dwell = node.dwell_modifier
                else:
                    node.dwell = max(self.train_type.default_train_dwell, node.timing_point.default_dwell)
            else:
                node.dwell = None
        # Dwell time is not applicable at the first and last locations.
        self.nodes[0].dwell = None
        self.nodes[-1].dwell = None
        
    def calculate_potential_speeds(self):
        # The link potential speed is the minimum of the train's top speed and the line speed. The node potential speed is the minimum of the train's top speed, the node's speed limit (which the user can input if a lower speed there is required, for example when crossing a junction) and the adjoining links' speed limits. This is unless the train stops at the location, in which case the node speed limit is set to zero.
        for link in self.links:            
            line_speed = link.edge.calculate_speed_limit(link.route_code)
            train_speed = self.train_type.top_speed
            link.potential = min(train_speed, line_speed)
        for node in self.nodes:            
            if node.halt:
                node.potential = 0
                # This will take care of the first and last locations, as their halt will already have been set to True.
            else:
                if node.node_speed_limit == None:
                    node.potential = min(self.train_type.top_speed, node.previous_link.potential, node.next_link.potential)
                else:
                    node.potential = min(self.train_type.top_speed, node.previous_link.potential, node.next_link.potential, node.node_speed_limit)
        
    def calculate_implied_speeds(self):
        # The "preimplied speed" at a location is the speed that the train can get up to there, given its speed at the previous location, its acceleration and its potential speed at the current location. This quantity is important when there are two or more timing points close together, because if the train is stopping at the first location but not the second, then its speed will still be low on passing the second location. The "postimplied speed" is similar to the preimplied speed, just the other way around. This quantity is important when there are two or more timing points close together, because then if the train is stopping at the second one but not the first, then its speed will already be low on passing the first location.
        self.nodes[0].preimplied_speed = 0
        for link in self.links:
            link.next_node.preimplied_speed = min(link.next_node.potential, sqrt(link.previous_node.preimplied_speed**2 + 2*self.train_type.acceleration*link.distance))
            # This uses the v^2=u^2+2as formula from schooldays.
        self.nodes[-1].postimplied_speed = 0
        for link in reversed(self.links.lister):
            link.previous_node.postimplied_speed = min(link.previous_node.potential, sqrt(link.next_node.postimplied_speed**2 + 2*self.train_type.deceleration*link.distance))
    
    def calculate_speeds_and_srts(self):
        self.calculate_potential_speeds()
        self.calculate_implied_speeds()
        for node in self.nodes:
            if node.potential == 0:
                node.speed = 0
            else:
                node.speed = min(node.preimplied_speed, node.postimplied_speed)
        for link in self.links:
            srt_calculator = SRTCalculator()
            initial_speed = link.previous_node.speed
            final_speed = link.next_node.speed
            acc = self.train_type.acceleration
            dec = self.train_type.deceleration
            link.speed_profile = srt_calculator.calculate_srt(initial_speed, final_speed, link.potential, link.distance, acc, dec)
            link.srt = link.speed_profile.srt
            link.speed = link.speed_profile.achieved_speed
            
    def calculate_runtimes(self):
        for link in self.links:
            if link.pathing == None:
                link.runtime = link.srt
            else:
                link.runtime = link.srt + link.pathing
                
    def calculate_arrivals_and_departures(self):
        self.nodes[0].arrival = None
        self.nodes[0].departure = 0
        for link in self.links:
            if link.next_node.halt:
                link.next_node.arrival = link.previous_node.departure + link.runtime
                if not link.next_node.finish_point:
                    link.next_node.departure = link.next_node.arrival + link.next_node.dwell
                else:
                    link.next_node.departure = None
            else:
                link.next_node.arrival = link.previous_node.departure + link.runtime
                link.next_node.departure = link.previous_node.departure + link.runtime
        self.exact_duration = self.nodes[-1].arrival
                
    def calculate_rounded_times(self):
        for node in self.nodes:
            if node.start_point:
                node.rounded_arrival = None
            else:
                node.rounded_arrival = 0.5*(node.arrival//0.5)
                if node.arrival % 0.5 > 0.499999:
                    node.rounded_arrival += 0.5
            if node.finish_point:
                node.rounded_departure = None
                if (node.rounded_arrival) % 1 == 0.5:
                    node.rounded_arrival = node.rounded_arrival + 0.5
                    self.half_adjustment = True
                else:
                    self.half_adjustment = False
                self.journey_time = int(node.rounded_arrival)
            else:
                node.rounded_departure = 0.5*((node.departure)//0.5)
                if node.departure % 0.5 > 0.499999:
                    node.rounded_departure += 0.5
        self.rounded_duration = self.nodes[-1].rounded_arrival

    def do_basic_calculations(self):
        self.calculate_halts()
        self.calculate_dwells()
        self.calculate_speeds_and_srts()
        self.calculate_runtimes()
        self.calculate_arrivals_and_departures()
        self.calculate_rounded_times()
        
    def create_trains_from_group(self):
        self.do_basic_calculations()
        self.trains = Lister()
        self.headcode_converter = HeadcodeConverter()
        start_time = self.principle_start_time
        while start_time <= datetime(1, 1, 3, 0, 0, 0):            
            headcode = self.headcode_converter.make_long_from_short(self.short_headcode, start_time)
            train = Train(self, headcode, start_time)
            train.finish_time = start_time + timedelta(minutes = self.rounded_duration)
            self.trains.append(train)
            start_time = start_time + timedelta(minutes = self.frequency)
    
    # The next three methods are used to provide detailed user output about a given train group.
    def assess_pathing(self):
        total_pathing = 0
        pathings = []
        for link in self.links:
            if link.pathing != None:
                total_pathing = total_pathing + link.pathing
                pathings.append([link.edge, link.pathing])
        self.total_pathing = total_pathing
        self.pathings = pathings
        
    def assess_non_default_dwell(self):
        total_over_dwell = 0
        total_under_dwell = 0
        over_dwells = []
        under_dwells = []
        for node in self.nodes:
            if node.dwell_modifier != None:
                extra_dwell = node.dwell_modifier - max(self.train_type.default_train_dwell, node.timing_point.default_dwell)
                if extra_dwell > 0:
                    total_over_dwell = total_over_dwell + extra_dwell
                    over_dwells.append([node.timing_point, extra_dwell])
                if extra_dwell < 0:
                    total_under_dwell = total_under_dwell - extra_dwell
                    under_dwells.append([node.timing_point, -extra_dwell])
        self.total_over_dwell = total_over_dwell
        self.total_under_dwell = total_under_dwell
        self.over_dwells = over_dwells
        self.under_dwells = under_dwells
        
    def calculate_flexing(self):
        self.assess_pathing()
        self.assess_non_default_dwell()
        self.flexing = self.total_pathing + self.total_over_dwell
        self.net_flexing = self.flexing - self.total_under_dwell

    # This is useful for creating graphs.
    def is_group_on_line_of_route(self, line_of_route):
        for link in self.links:
            if link.edge in line_of_route.all_edges:
                return True
        return False
        
    # This is useful for creating departure boards.
    def is_at(self, timing_point):
        for node in self.nodes:
            if node.timing_point == timing_point:
                return True
        return False
