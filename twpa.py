import re
import os

directory = '.'
files = os.listdir(directory)

word_list = []

WORD_WEIGHT = 3

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
        pattern_re = re.findall(r'.*',line)
        pattern_for_utterance = "".join(pattern_re)
        utterance = pattern_for_utterance.split()
        for word in utterance:
            if len(word) >= WORD_WEIGHT:
                n = 0
                equal_file = False
                while n < len(word_list):
                    if word_list[n] == word:
                        equal_file = True
                    n += 1
                if equal_file == False:
                    word_list.append(word)
                else:
                    equal_file = False

    f.close()
    

print_files_on_dir("CSV") #files in dir
file_number = int(input())
copy_rules_from_file(str(files[file_number]))

word_list = sorted(word_list)
print (word_list)
