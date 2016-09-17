from csv import reader
from TT_basics_tools import Lister, Finder
from TT_translators_schedules import GroupTranslator

# We create a group controller to store schedule input in a helpful way.

class GroupController(Finder):
    
    def __init__(self):
        Finder.__init__(self)
        
# We create a tool that will import a file of train groups.

class ScheduleLoader(object):

    def __init__(self, data_controllers):
        self.data_controllers = data_controllers
        self.group_translator = GroupTranslator(self.data_controllers)
        
    def import_schedules(self, group_filename):
        group_controller = GroupController()
        with open(group_filename) as group_file:
            group_reader = reader(group_file, delimiter='}')
            group_lines = []
            for line in group_reader:
                if line != ['%End of record']:
                    if line == []:
                        group_lines.append('')
                    else:
                        group_lines.append(line[0])
                else:
                    if len(group_lines) > 7:
                        print group_lines[0]
                    short_headcode_string, train_type_string, note_line, association_string, principle_start_time_string, frequency_string, journey_line = group_lines
                    group = self.group_translator.decode(short_headcode_string, train_type_string, note_line, association_string, principle_start_time_string, frequency_string, journey_line)
                    group_controller[group.short_headcode.short_headcode_string] = group
                    group_lines = []
        return group_controller
        
    def export_schedules(self, group_controller, group_filename):
        group_file = open(group_filename, 'w')
        for group in group_controller:
            short_headcode_string, train_type_string, note_line, association_string, principle_start_time_string, frequency_string, journey_line = self.group_translator.encode(group)
            group_file.write(short_headcode_string)
            group_file.write('\n')
            group_file.write(train_type_string)
            group_file.write('\n')
            group_file.write(note_line)
            group_file.write('\n')
            group_file.write(association_string)
            group_file.write('\n')
            group_file.write(principle_start_time_string)
            group_file.write('\n')
            group_file.write(frequency_string)
            group_file.write('\n')
            group_file.write(journey_line)
            group_file.write('\n')
            group_file.write('%End of record')
            group_file.write('\n')
        group_file.close()
