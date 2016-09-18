from TT_translators_schedules import TimeTranslator

# This is a tool that displays schedule details.

class ScheduleShower(object):

    def __init__(self, group_controller):
        self.group_controller = group_controller

    def show_pathing(self, group):
        group.calculate_flexing()
        for edge, pathing in group.pathings:
            print 'This schedule has %s minutes\' pathing on %s.' % (pathing, edge.name)

    def show_deficiency(self, group):
        group.calculate_flexing()
        for timing_point, deficiency in group.under_dwells:
            print 'This schedule has a %s-minute deficiency in dwell at %s.' % (deficiency, timing_point.name)

    def show_low_association(self, group):
        low = False
        if group.short_headcode.short_headcode_string[0] == '5':
            if group.city_starter:
                if group.association < 9:
                    low = True
            else:
                if group.association < 5:
                    low = True
        if group.short_headcode.short_headcode_string[0] != '1':
            if group.city_starter:
                if group.association < 7:
                    low = True
            else:
                if group.short_headcode.short_headcode_string[0] == '3' and group.association < 3:
                    low = True
        else:
            if group.city_starter:
                if group.association < 18:
                    low = True
        if low:
            print group.short_headcode.short_headcode_string
            print 'This schedule only has an association of %s minutes at %s.' % (str(group.association), group.first_timing_point.name)

    def show_extra_dwells(self, group):
        group.calculate_flexing()
        for timing_point, extra_dwell in group.over_dwells:
            print 'This schedule has %s minutes\' extra dwell at %s.' % (extra_dwell, timing_point.name)

    def show_flexing(self, group):
        self.show_deficiency(group)
        self.show_extra_dwells(group)
        self.show_pathing(group)
        if len(group.pathings) == 0 and len(group.under_dwells) == 0 and len(group.over_dwells) == 0:
            print 'This schedule has not been flexed at all.'
        if group.half_adjustment:
            print 'An adjustment of {0.5} has been added at the final location to finish on a whole minute.'

    def list_overtimed_groups(self):
        for group in self.group_controller:
            if group.train_type.passenger and group.short_headcode.short_headcode_string[0] != '5':
                group.do_basic_calculations()
                group.calculate_flexing()
                flex = group.net_flexing
                if group.half_adjustment:
                    flex = flex + 0.5
                if flex >= 1:
                    print group.short_headcode.short_headcode_string
                    self.show_flexing(group)

    def list_deficient_groups(self):
        for group in self.group_controller:
            if group.train_type.passenger:
                group.calculate_flexing()
                if len(group.under_dwells) != 0:
                    print group.short_headcode.short_headcode_string
                    self.show_deficiency(group)

    def list_low_associations(self):
        for group in self.group_controller:
            if group.train_type.passenger:
                self.show_low_association(group)
        
    def display_train_schedule(self, train):
        time_translator = TimeTranslator()
        train.calculate_timings()
        print '\n%s: %s to %s' % (train.headcode.headcode_string, train.group.nodes[0].timing_point.name, train.group.nodes[-1].timing_point.name)
        if train.group.notes.length != 0:
            for note in train.group.notes:
                print note
                print ''
        
        for train_node in train.train_nodes:
            node_strings = []
            if train_node.arrival == None:
                arrival_string = '******'
            elif train_node.group_node.halt == False:
                arrival_string = '------'
            else:
                arrival_string = time_translator.half_encode(train_node.arrival)
            node_strings.append(arrival_string)
            if train_node.departure == None:
                departure_string = '******'
            else:
                departure_string = time_translator.half_encode(train_node.departure)
            node_strings.append(departure_string)
            node_strings.append(train_node.name)
            if train_node.group_node.platform != None:
                platform_string = '- platform %s' % train_node.group_node.platform
                node_strings.append(platform_string)
            if train_node.group_node.halt == False:
                pass_string = '(pass at %s mph)' % int(60*train_node.group_node.speed)
                node_strings.append(pass_string)

            link_strings = []
            if train_node.group_node.route_code_changes:
                link_strings.append(train_node.group_node.next_link.route_code.name)
            if not train_node.group_node.finish_point:
                if train_node.group_node.next_link.pathing != None:
                    pathing_string = '(%s)' % train_node.group_node.next_link.pathing
                    link_strings.append(pathing_string)
            if not train_node.group_node.finish_point:
                if train_node.group_node.next_link.next_node.finish_point:
                    if train.group.half_adjustment:
                        link_strings.append('{0.5}')

            print ' '.join(node_strings)
            if len(link_strings) != 0:
                print ' '.join(link_strings)

        print '\nThe journey time is %s minutes.' % train.group.journey_time

    def show_schedule(self):
        short_headcode_string = raw_input('Please give the short headcode of the train group. ')
        train_number = input('Which number train of the group would you like the schedule of? ')
        group = self.group_controller[short_headcode_string]
        group.create_trains_from_group()
        train = group.trains[train_number]
        self.display_train_schedule(train)
        self.show_flexing(group)
