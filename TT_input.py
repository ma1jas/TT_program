from TT_input_schedules import ScheduleInputter
from TT_input_data import DataInputter

class Inputter(object):

    def __init__(self, data_controllers, group_controller):
        self.data_controllers = data_controllers
        self.group_controller = group_controller
        
    def do_input(self):
        choice = raw_input('\nHit "r" to edit route codes.\nHit "t" to edit timing points.\nHit "e" to edit edges.\nHit "l" to edit lines of route.\nHit "y" to edit train types.\nHit "s" edit schedules.\nHit "p" not to edit anything.')
        if choice in set(['r', 't', 'e', 'l', 'y']):
            data_inputter = DataInputter(self.data_controllers)
            data_inputter.input_data(choice)
        if choice == 's':
            schedule_inputter = ScheduleInputter(self.data_controllers, self.group_controller)
            schedule_inputter.input_schedule()
        if choice == 'p':
            pass
