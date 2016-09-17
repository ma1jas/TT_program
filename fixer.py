# This program opens a .csv data file, makes various changes to it and then spits it back out again in its corrected state.

import csv

fix_this = []

with open('timetable_data_scheduleinput.csv') as file_to_correct:
    to_be_fix_this = csv.reader(file_to_correct, delimiter = ',')
    
    for line in to_be_fix_this:
        fix_this.append(line)

# This has now read the entire file into a list of lines called fix_this.

# print fix_this

n = len(fix_this)

for i in range(n):
    
    if ':' in str(fix_this[i]):
        new_line = ['15']
        new_line.append(fix_this[i])
        fix_this[i] = new_line
        
# fix_this is the list of lines that we now want to write back to a .csv file.

output_file = open('filename_here.csv', 'w')

for i in range(n - 1):
    if fix_this[i] == []:
        output_file.write('\n')
    else:
        if len(fix_this[i]) == 2:
                output_file.write(str(fix_this[i][1][0]))
                output_file.write(',')
                output_file.write(str(fix_this[i][0]))
                output_file.write('\n')
        else:
            for j in range(len(fix_this[i]) - 1):
                output_file.write(str(fix_this[i][j]))
                output_file.write(',')
            output_file.write(str(fix_this[i][-1]))
            output_file.write('\n')
output_file.write(str(fix_this[-1][0]))

output_file.close()
