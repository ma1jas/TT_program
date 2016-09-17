from TT_load_data import DataLoader
from TT_load_schedules import ScheduleLoader

class Loader(object):

    def import_all(self, filenames_in):
        data_filenames_in = filenames_in[:-1]
        group_filename = filenames_in[-1]
        data_loader = DataLoader()
        data_controllers = data_loader.import_data(data_filenames_in)
        schedule_loader = ScheduleLoader(data_controllers)
        group_controller = schedule_loader.import_schedules(group_filename)
        return data_controllers, group_controller
        
    def export_all(self, data_controllers, group_controller, filenames_out):
        data_filenames_out = filenames_out[:-1]
        group_filename = filenames_out[-1]
        data_loader = DataLoader()
        data_loader.export_data(data_controllers, data_filenames_out)
        schedule_loader = ScheduleLoader(data_controllers)
        schedule_loader.export_schedules(group_controller, group_filename)
