from __future__ import division
from datetime import datetime
from TT_basics_tools import SplitStripper, Lister
from TT_basics_data import ShortHeadcode, Notes
from TT_basics_groups import Node, LinkModifier, Link, JourneySpec, Group

# We create a tool that translates train note input and output.

class NoteTranslator(object):

    def decode(self, note_line):
        split_stripper = SplitStripper()
        notes = Notes()
        note_strings = split_stripper.split_strip(note_line, ';')
        for note_string in note_strings:
            notes.add_item(note_string)
        return notes
        
    def encode(self, notes):
        note_strings = []
        for note in notes:
            note_strings.append(note)
        note_line = ';'.join(note_strings)
        return note_line
                
# We create a tool that translates time input and output.

class TimeTranslator(object):

    def decode(self, time_string):
        split_stripper = SplitStripper()
        time_strings = split_stripper.split_strip(time_string, ':')
        hours = int(time_strings[0])
        minutes = int(time_strings[1])
        time = datetime(1, 1, 2, hours, minutes, 0)
        return time
        
    def encode(self, time):
        hour_string = str(time.hour)
        minute_string = str(time.minute)
        if len(hour_string) == 1:
            hour_string = ''.join(['0', hour_string])
        if len(minute_string) == 1:
            minute_string = ''.join(['0', minute_string])
        time_string = ''.join([hour_string, ':', minute_string])
        return time_string
        
    def exact_encode(self, time):
        time_string = self.encode(time)
        seconds = int(time.second)
        second_string = str(seconds)
        if len(second_string) == 1:
            second_string = ''.join(['0', second_string])
        exact_time_string = ''.join([time_string, ':', second_string])
        return exact_time_string

    def half_encode(self, time):
        time_string = self.encode(time)
        seconds = int(time.second)
        if seconds < 30:
            half_time_string = ''.join([time_string, ' '])
        else:
            half_time_string = ''.join([time_string, u'\u00bd'])
        return half_time_string

# We create a tool that translates schedule frequency input and output.

class FrequencyTranslator(object):

    def decode(self, frequency_string):
        frequency_string = frequency_string.strip()
        if frequency_string == 'x':
            frequency = 1440
        else:
            stripped_frequency_string = frequency_string.strip(' minutes')
            frequency = int(stripped_frequency_string)
        return frequency

    def encode(self, frequency):
        if frequency == 1440:
            frequency_string = 'x'
        else:
            frequency_string = ''.join([str(frequency), ' minutes'])
        return frequency_string

# We create a tool that translates between stop modifiers and halt and dwell modifiers.

class ModifierTranslator(object):

    def decode(self, stop_modifier):
        if stop_modifier == 'x':
            halt_modifier = False
            dwell_modifier = None
        else:
            if stop_modifier == '':
                halt_modifier = None
                dwell_modifier = None
            else:
                halt_modifier = True
                stripped_stop_modifier = stop_modifier.strip('d')
                dwell_modifier = float(stripped_stop_modifier)                
        return halt_modifier, dwell_modifier
                
    def encode(self, halt_modifier, dwell_modifier):
        if halt_modifier == False:
            stop_modifier = 'x'
        else:
            if dwell_modifier != None:
                stop_modifier = ''.join(['d', str(dwell_modifier)])
            else:
                stop_modifier = ''   
        return stop_modifier

# We create a tool that translates journey node input and output.

class NodeTranslator(object):

    def __init__(self, timing_point_controller):
        self.timing_point_controller = timing_point_controller
        self.modifier_translator = ModifierTranslator()

    def decode(self, node_line):
        split_stripper = SplitStripper()
        split_node_entry = split_stripper.split_strip(node_line, ',')
        timing_point_string = split_node_entry[0]
        timing_point = self.timing_point_controller[timing_point_string]
        platform = None
        stop_modifier = ''
        node_speed_limit = None
        for item in split_node_entry[1:]:
            if 'mph' in item:
                node_speed_limit_string = item.strip('mph')
                node_speed_limit = float(node_speed_limit_string)/60
            elif item == 'x':
                stop_modifier = item
            elif item[0] == 'd':
                stop_modifier = item
            else:
                platform = item
        halt_modifier, dwell_modifier = self.modifier_translator.decode(stop_modifier)
        node = Node(timing_point, platform, halt_modifier, dwell_modifier, node_speed_limit)
        return node
        
    def encode(self, node):
        node_strings = [node.timing_point.name]
        if node.platform != None:
            node_strings.append(node.platform)            
        stop_modifier = self.modifier_translator.encode(node.halt_modifier, node.dwell_modifier)
        if stop_modifier != '':
            node_strings.append(stop_modifier)
        if node.node_speed_limit != None:
            node_speed_limit_string = ''.join([str(60*node.node_speed_limit), 'mph'])
            node_strings.append(node_speed_limit_string)
        node_line = ','.join(node_strings)
        return node_line
        
# We create a tool that translates journey link input and output.

class LinkModifierTranslator(object):

    def __init__(self, route_code_controller):
        self.route_code_controller = route_code_controller
    
    def decode(self, link_string):
        split_stripper = SplitStripper()
        split_link_entry = split_stripper.split_strip(link_string, ',')
        route_code = None
        pathing = None
        for item in split_link_entry:
            if '(' in item:
                pathing_string = item.strip('()')
                pathing = float(pathing_string)
            else:
                route_code_name = item
                route_code = self.route_code_controller[route_code_name]
        link_modifier = LinkModifier(route_code, pathing)
        return link_modifier
        
    def encode(self, link_modifier):
        link_strings = []
        if link_modifier.route_code != None:
            route_code_name = link_modifier.route_code.name
            link_strings.append(route_code_name)
        pathing_string = ''
        if link_modifier.pathing != None:
            pathing_string = ''.join(['(', str(link_modifier.pathing), ')'])
            link_strings.append(pathing_string)
        link_line = ','.join(link_strings)
        return link_line

# We create a tool that translates journey input and output.
        
class JourneyTranslator(object):

    def __init__(self, route_code_controller, timing_point_controller):
        self.route_code_controller = route_code_controller
        self.timing_point_controller = timing_point_controller
        self.split_stripper = SplitStripper()
        self.node_translator = NodeTranslator(self.timing_point_controller)
        self.link_modifier_translator = LinkModifierTranslator(self.route_code_controller)

    def is_this_a_node_entry(self, entry):
        split_entry = self.split_stripper.split_strip(entry, ',')
        first_item = split_entry[0]
        if first_item[0] == '(':
            return False
        if first_item in self.route_code_controller.route_code_names:
            return False
        else:
            return True
            
    def decode(self, journey_line):
        split_journey = self.split_stripper.split_strip(journey_line, ';')
        journey_spec = JourneySpec()
        for entry in split_journey:
            this_is_a_node_entry = self.is_this_a_node_entry(entry)
            if this_is_a_node_entry == True:
                node = self.node_translator.decode(entry)
                journey_spec.add_item(node)
            else:
                link_modifier = self.link_modifier_translator.decode(entry)
                journey_spec.add_item(link_modifier)
        return journey_spec

    def encode(self, journey_spec):
        journey_strings = []
        for journey_item in journey_spec:
            if isinstance(journey_item, Node):
                node_line = self.node_translator.encode(journey_item)
                journey_strings.append(node_line)
            if isinstance(journey_item, LinkModifier):
                link_line = self.link_modifier_translator.encode(journey_item)
                journey_strings.append(link_line)
        journey_line = ';'.join(journey_strings)
        return journey_line

# However, the user only inputs a link when the route code changes or where there is pathing. A train group will need a link between each pair of nodes, so we create a journey converter to provide this.

class JourneyConverter(object):

    def convert(self, journey_spec):
        nodes = Lister()
        links = Lister()
        just_had_a_node = False
        last_route_code = None
        for journey_item in journey_spec:
            if isinstance(journey_item, Node):
                if just_had_a_node:
                    link = Link(last_route_code, None)
                    links.add_item(link)
                node = journey_item
                nodes.add_item(node)
                just_had_a_node = True
            if isinstance(journey_item, LinkModifier):
                if journey_item.route_code == None:
                    link = Link(last_route_code, journey_item.pathing)
                else:
                    link = Link(journey_item.route_code, journey_item.pathing)
                    last_route_code = link.route_code
                links.add_item(link)
                just_had_a_node = False
        return nodes, links
        
    def relate_nodes_and_links(self, nodes, links, edge_controller):
        for node in nodes:
            node.start_point = False
            node.finish_point = False
            node.end_point = False
        nodes[0].start_point = True
        nodes[0].end_point = True
        nodes[-1].finish_point = True
        nodes[-1].end_point = True
        
        for index in range(links.length):
            nodes[index + 1].previous_link = links[index]
            nodes[index].next_link = links[index]
            links[index].previous_node = nodes[index]
            links[index].next_node = nodes[index + 1]
        
        for node in nodes:
            node.route_code_changes = False
            if node.start_point:
                node.route_code_changes = True
            elif node.finish_point:
                node.route_code_changes = False
            else:
                if node.previous_link.route_code != node.next_link.route_code:
                    node.route_code_changes = True
                if node.timing_point.platform_routes[node.platform] != None:
                    if node.timing_point.platform_routes[node.platform] != node.next_link.route_code:
                        node.route_code_changes = True
                              
        for link in links:
            tp_from = link.previous_node.timing_point
            tp_to = link.next_node.timing_point
            link.edge = edge_controller[(link.previous_node.timing_point, link.next_node.timing_point)]
            if link.edge == None:
                print link.previous_node.timing_point.name, link.next_node.timing_point.name
            link.distance = link.edge.edge_length
            
    def convert_back(self, nodes, links):
        journey_spec = JourneySpec()
        journey_spec.add_item(nodes[0])
        for link in links:
            if link.pathing != None or link.previous_node.route_code_changes:
                if link.previous_node.route_code_changes:
                    link_modifier = LinkModifier(link.route_code, link.pathing)
                else:
                    link_modifier = LinkModifier(None, link.pathing)
                journey_spec.add_item(link_modifier)
            journey_spec.add_item(link.next_node)
        return journey_spec

# We create a tool that translates train group specification input and output.

class GroupTranslator(object):
    
    def __init__(self, data_controllers):
        self.data_controllers = data_controllers
        self.note_translator = NoteTranslator()
        self.time_translator = TimeTranslator()
        self.frequency_translator = FrequencyTranslator()
        self.journey_translator = JourneyTranslator(self.data_controllers.route_code_controller, self.data_controllers.timing_point_controller)
        self.journey_converter = JourneyConverter()
    
    def decode(self, short_headcode_string, train_type_string, note_line, association_string, principle_start_time_string, frequency_string, journey_line):
        short_headcode = ShortHeadcode(short_headcode_string)
        train_type = self.data_controllers.train_type_controller[train_type_string]
        notes = self.note_translator.decode(note_line)
        association = int(association_string)
        principle_start_time = self.time_translator.decode(principle_start_time_string)
        frequency = self.frequency_translator.decode(frequency_string)
        journey_spec = self.journey_translator.decode(journey_line)
        nodes, links = self.journey_converter.convert(journey_spec)
        self.journey_converter.relate_nodes_and_links(nodes, links, self.data_controllers.edge_controller)
        group = Group(short_headcode, train_type, notes, association, principle_start_time, frequency, nodes, links)
        return group
        
    def encode(self, group):
        short_headcode_string = group.short_headcode.short_headcode_string
        train_type_string = group.train_type.name
        note_line = self.note_translator.encode(group.notes)
        association_string = str(group.association)
        principle_start_time_string = self.time_translator.encode(group.principle_start_time)
        frequency_string = self.frequency_translator.encode(group.frequency)
        journey_spec = self.journey_converter.convert_back(group.nodes, group.links)
        journey_line = self.journey_translator.encode(journey_spec)
        return short_headcode_string, train_type_string, note_line, association_string, principle_start_time_string, frequency_string, journey_line
