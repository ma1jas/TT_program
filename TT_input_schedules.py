from TT_translators_schedules import GroupTranslator

class ScheduleInputter(object):

    def __init__(self, data_controllers, group_controller):
        self.data_controllers = data_controllers
        self.group_controller = group_controller
        
    def create_schedule(self):
        group_translator = GroupTranslator(self.data_controllers)
        short_headcode_string = raw_input('Please give the short headcode of the train group. ')
        train_type_string = raw_input('Please give the train type. ')
        notes_line = raw_input('Please type any required notes for this train group, separated by commas. ')
        association_string = raw_input('Please give the association (from the previous working). ')
        principle_start_time_string = raw_input('Please give the origin time of the first train in the group, in the format HH:MM. ')
        frequency_string = raw_input('Please give the frequency interval of the train group. (If there is to be only one train per day, please hit "x" instead.) ')
        journey_input_instructions = 'Please enter the required timing points, separated by semicolons. You can choose to give accompanying platform numbers, stop modifiers and point speeds, separated from the timing point by commas. The stop modifier "x" forces a pass through, while "d" with a number will force a stop for that number of minutes. You can change the route code between timing points by simply typing the new route code, while a number in brackets will produce that number of minutes\' pathing time. It is compulsory to provide a route code between the first two timing points.\nIf you\'re totally lost, then just hit "x" for an example.'
        user_input = raw_input(journey_input_instructions)
        if user_input == 'x':
            more_instructions = 'A typical example would be something like the following:\n\nAnytown,13; FL; Little Village,1,x; Crossover Junction; Another Village,1,x,75mph; SL; New Town,3,d2; Country Halt,x; Big Station,12\n\nThe "x"s mean that the train passes through Little Village, Another Village and Country Halt, even though they are stations. Crossover Junction does not need an "x" because it is not a default stopping location. The d2 means that the train would stop at New Town for 2 minutes. The rest should hopefully be obvious.\nNow come on, get on with it.'
            user_input = raw_input(more_instructions)
        journey_line = user_input
        group = group_translator.decode(short_headcode_string, train_type_string, notes_line, association_string, principle_start_time_string, frequency_string, journey_line)
        self.group_controller[short_headcode_string] = group
        
    def delete_schedule(self):        
        short_headcode_string = raw_input('Please give the short headcode of the train group that you want to delete. ')
        confirm = raw_input('Hit "y" if you are sure that you want to delete train group %s.' % (short_headcode_string))
        if confirm == 'y':
            self.group_controller.delete(short_headcode_string)
            
    def input_schedule(self):
        choice = raw_input('Hit "n" to create a train schedule.\nHit "d" to delete one.\nHit "p" not to make any changes.\n\n')
        if choice == 'n':
            self.create_schedule()
        if choice == 'd':
            self.delete_schedule()
        if choice == 'p':
            pass
