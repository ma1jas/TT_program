from TT_load import Loader
from TT_input import Inputter
from TT_output import Outputter

filenames_in = ['../TT_data/TT_data_routecodes.csv', '../TT_data/TT_data_timingpoints.csv', '../TT_data/TT_data_edges.csv', '../TT_data/TT_data_linesofroute.csv', '../TT_data/TT_data_traintypes.csv', '../TT_data/TT_data_scenes.csv', '../TT_data/TT_data_schedules.csv']
filenames_out = ['../TT_data/TT_data_routecodes.csv', '../TT_data/TT_data_timingpoints.csv', '../TT_data/TT_data_edges.csv', '../TT_data/TT_data_linesofroute.csv', '../TT_data/TT_data_traintypes.csv', '../TT_data/TT_data_schedules.csv']

loader = Loader()
data_controllers, group_controller = loader.import_all(filenames_in)

# inputter = Inputter(data_controllers, group_controller)
# inputter.do_input()

outputter = Outputter(data_controllers, group_controller)
export = outputter.do_output()

if export:
    loader.export_all(data_controllers, group_controller, filenames_out)
