from __future__ import division
from datetime import datetime, timedelta
from math import sqrt
from TT_basics_tools import Lister
from TT_basics_data import Headcode

# We create a tool that converts between headcodes and short headcodes.

class HeadcodeConverter(object):
    
    def __init__(self):
        self.fifth_character_dict = {0:'A', 1:'B', 2:'C', 3:'D', 4:'E', 5:'F', 6:'G', 7:'H', 8:'I', 9:'J', 10:'K', 11:'L', 12:'M', 13:'N', 14:'O', 15:'P', 16:'Q', 17:'R', 18:'S', 19:'T', 20:'U', 21:'V', 22:'W', 23:'X'}
        self.sixth_character_dict = {0:'A', 1:'A', 2:'A', 3:'A', 4:'A', 5:'A', 6:'A', 7:'A', 8:'A', 9:'A', 10:'A', 11:'A', 12:'A', 13:'A', 14:'A', 15:'B', 16:'B', 17:'B', 18:'B', 19:'B', 20:'B', 21:'B', 22:'B', 23:'B', 24:'B', 25:'B', 26:'B', 27:'B', 28:'B', 29:'B', 30:'C', 31:'C', 32:'C', 33:'C', 34:'C', 35:'C', 36:'C', 37:'C', 38:'C', 39:'C', 40:'C', 41:'C', 42:'C', 43:'C', 44:'C', 45:'D', 46:'D', 47:'D', 48:'D', 49:'D', 50:'D', 51:'D', 52:'D', 53:'D', 54:'D', 55:'D', 56:'D', 57:'D', 58:'D', 59:'D'}
        
    def make_long_from_short(self, short_headcode, start_time):
        short_headcode_string = short_headcode.short_headcode_string
        fifth_character = self.fifth_character_dict[start_time.hour]
        sixth_character = self.sixth_character_dict[start_time.minute]
        headcode_string = ''.join([short_headcode_string, fifth_character, sixth_character])
        headcode = Headcode(headcode_string, short_headcode)
        return headcode

class TrainNode(object):

    def __init__(self, group_node):
        self.group_node = group_node
        self.name = self.group_node.timing_point.name

class Train(object):

    def __init__(self, group, headcode, start_time):
        self.group = group
        self.headcode = headcode
        self.train_type = group.train_type
        self.notes = group.notes
        self.start_time = start_time
        self.finish_time = self.start_time + timedelta(minutes = self.group.journey_time)
        self.train_nodes = Lister()
        for group_node in self.group.nodes:
            train_node = TrainNode(group_node)
            self.train_nodes.append(train_node)
                    
    def calculate_timings(self):
        for train_node in self.train_nodes:
            if train_node.group_node.arrival != None:
                train_node.arrival = self.start_time + timedelta(minutes = train_node.group_node.rounded_arrival)
                train_node.exact_arrival = self.start_time + timedelta(minutes = train_node.group_node.arrival)
                if train_node.arrival.second == 0:
                    train_node.public_arrival = train_node.arrival
                else:
                    assert train_node.arrival.second == 30
                    train_node.public_arrival = train_node.arrival + timedelta(seconds = 30)
            else:
                train_node.arrival = None
                train_node.exact_arrival = None
                train_node.public_arrival = None
                
            if train_node.group_node.departure != None:
                train_node.departure = self.start_time + timedelta(minutes = train_node.group_node.rounded_departure)
                train_node.exact_departure = self.start_time + timedelta(minutes = train_node.group_node.departure)
                if train_node.departure.second == 0:
                    train_node.public_departure = train_node.departure
                else:
                    assert train_node.departure.second == 30
                    train_node.public_departure = train_node.departure - timedelta(seconds = 30)
            else:
                train_node.departure = None
                train_node.exact_departure = None
                train_node.public_departure = None

        # This is useful for creating departure boards.
    def train_nodes_corresponding_to_tp(self, timing_point):
        corresponding_train_nodes = set([])
        for train_node in self.train_nodes:
            if train_node.group_node.timing_point == timing_point:
                corresponding_train_nodes.add(train_node)
        return corresponding_train_nodes
