# We create a "list object" class, so as later to be able to instantiate self-contained list objects.
            
class Lister(object):
    
    def __init__(self):
        self.lister = []
    
    @property
    def length(self):
        return len(self.lister)
        
    def add_item(self, item):
        self.lister.append(item)
        
    def delete_item(self, item):
        self.lister.remove(item)
        
    def __getitem__(self, reference):
        return self.lister[reference]
        
    def is_it_empty(self):
        if self.length == 0:
            return True
        else:
            return False

# We create a "dictionary object" class, so as later to be able to instantiate self-contained dictionary objects.

class Finder(object):

    def __init__(self):
        self.finder = {}
        
    @property
    def length(self):
        return len(self.finder)
    
    def __setitem__(self, key, value):
        self.finder[key] = value
                
    def delete(self, key):
        self.finder.__delitem__(key)
    
    def __getitem__(self, key):
        if key in self.finder:
            return self.finder[key]
            
    def __iter__(self):
        return self.finder.itervalues()
                    
    def is_it_empty(self):
        if self.length == 0:
            return True
        else:
            return False
            
# We create a tool that takes a list of strings and strips all whitespace from its elements.

class SplitStripper(object):

    def split_strip(self, input_string, separator):
        stripped_list = []
        split_string_list = input_string.split(separator)
        for item in split_string_list:
            stripped_item = item.strip()
            stripped_list.append(stripped_item)
        return stripped_list
        
# We now introduce a tool that takes an integer list and counts how long each non-zero block and each zero block is. We assume that we start and end with (possibly empty) zero blocks. So [1, 12, 0, 0, 0, -4, 0, 0, 0, 0, 1] would return [2, 1, 1], [0, 3, 4, 0].

class ZeroBlockMeasurer(object):

    def record_lengths_of_zero_blocks(self, integers):
        true_block_length = 0
        false_block_length = 0
        true_block_lengths = []
        false_block_lengths = []
        previous_integer = False
        for integer in integers:
            if integer != 0:
                if previous_integer != 0:
                    true_block_length = true_block_length + 1
                else:
                    false_block_lengths.append(false_block_length)
                    false_block_length = 0
                    true_block_length = 1
                    previous_integer = integer
            else:
                if previous_integer != 0:
                    true_block_lengths.append(true_block_length)
                    true_block_length = 0
                    false_block_length = 1
                    previous_integer = integer
                else:
                    false_block_length = false_block_length + 1
        if true_block_length != 0:
            true_block_lengths.append(true_block_length)
        false_block_lengths.append(false_block_length)
        return true_block_lengths, false_block_lengths
