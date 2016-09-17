from TT_output_datashower import DataShower
from TT_output_scheduleshower import ScheduleShower
from TT_output_departureboarddisplayer import DepartureboardDisplayer
from TT_output_realtimeshower import RealtimeShower
from TT_output_visualiser import Visualiser
from TT_output_graphdrawer import GraphDrawer
from TT_output_cityaccessshower import CityaccessShower
from TT_output_platformshower import PlatformShower
from TT_output_shunter import Shunter
from TT_check_data import DataChecker

class Outputter(object):

    def __init__(self, data_controllers, group_controller):
        self.data_controllers = data_controllers
        self.group_controller = group_controller
        self.export = False
        
    def do_output(self):
        choice = raw_input('\nHit "i" to show infrastructure data.\nHit "s" to show a train schedule.\nHit "z" to investigate overtimed schedules.\nHit "e" to investigate deficiencies in schedules.\nHit "g" to show a graph.\nHit "j" to produce a set of screenshots of all the graphs.\nHit "d" to show a departure board at a particular location.\nHit "r" to show real-time events at a timing point.\nHit "v" to see a real-time visualisation of a part of the rail network.\nHit "a" to see how many trains per hour each timing point has.\nHit "c" to investigate the services from a station to the city.\nHit "p" to show the platforms used at a timing point.\nHit "u" to make a shunt move.\nHit Space not to make any outputs.\n\nYou can show default graphs more quickly: hit "f", "t" or "h" followed by the line of route number to show a half-hour, three-quarter, or hour graph of the corresponding line of route that starts at midday.\n\nOr, type "check" to run checks on the data.\n')
        if choice == 'i':
            data_shower = DataShower(self.data_controllers)
            data_shower.show_data()
        if choice == 's':
            schedule_shower = ScheduleShower(self.group_controller)
            schedule_shower.show_schedule()
        if choice == 'z':
            schedule_shower = ScheduleShower(self.group_controller)
            schedule_shower.list_overtimed_groups()
        if choice == 'e':
            schedule_shower = ScheduleShower(self.group_controller)
            schedule_shower.list_deficient_groups()
            schedule_shower.list_low_associations()
        if choice == 'd':
            departureboard_displayer = DepartureboardDisplayer(self.data_controllers, self.group_controller)
            departureboard_displayer.display_departureboard()
        if choice == 'r':
            realtime_shower = RealtimeShower(self.data_controllers, self.group_controller)
            realtime_shower.show_realtime()
        if choice == 'v':
            visualiser = Visualiser(self.data_controllers, self.group_controller)
            visualiser.show_visualisation()
        if choice == 'a':
            departureboard_displayer = DepartureboardDisplayer(self.data_controllers, self.group_controller)
            departureboard_displayer.count_stops()
        if choice == 'c':
            cityaccess_shower = CityaccessShower(self.data_controllers, self.group_controller)
            cityaccess_shower.show_cityaccess()
        if choice == 'p':
            platform_shower = PlatformShower(self.data_controllers, self.group_controller)
            platform_shower.show_platforms()
        if choice == 'u':
            shunter = Shunter(self.data_controllers, self.group_controller)
            shunter.make_shunt()
            self.export = True
        if choice[0] in {'g', 'f', 't', 'h', 'j'}:
            graph_drawer = GraphDrawer(self.data_controllers, self.group_controller)
            graph_drawer.draw_graph(choice)
        if choice == " ":
            pass
        if choice == 'check':
            data_checker = DataChecker(self.data_controllers, self.group_controller)
            data_checker.check_data()
        return self.export
