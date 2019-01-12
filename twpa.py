import re
import os

directory = '.'
files = os.listdir(directory)

rule_list = []


def print_files_on_dir(text):
    n = 0   
    print ('')
    print ('')
    print ('===List of files===')
    print ('')
    print ('')
    while n < len(files):
        name_of_file = files[n]
        result_string = "[" + str(n) + "]" + " - " + name_of_file
        print (result_string)
        n += 1
    print ('')
    print ('')
    print ('===================')
    print ('')
    final_message = "Select " + text + " with tests. Enter the number:"
    print (final_message)

def copy_rules_from_file(file_path):
    f = open(file_path, 'r', encoding='utf8')
    
    for line in f:
        pattern_for_rules = re.findall(r'.*',line)
        pattern_for_rules2 = "".join(pattern_for_rules)
        utterance = pattern_for_rules2.split()
        for word in utterance:
            if len(word) >= 3:
                print (word)

        n = 0
        equal_file = False
        while n < len(rule_list):
            if rule_list[n] == pattern_for_rules:
                equal_file = True
            n += 1
        if equal_file == False:
            rule_list.append(pattern_for_rules)
        else:
            equal_file = False

    f.close()
    n = 0

print_files_on_dir("CSV") #files in dir
file_number = int(input())
copy_rules_from_file(str(files[file_number]))
