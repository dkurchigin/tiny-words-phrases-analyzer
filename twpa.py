import re
import os
import sqlite3

directory = '.'
files = os.listdir(directory)

word_list = []

WORD_WEIGHT = 3

def check_db_exist(file_path):
    print(file_path)
    base_extension = ".db"
    file_path = file_path + base_extension
    if os.path.isfile(file_path):
        os.remove(file_path)
        print("Delete older version of", file_path)
    create_db(file_path)
    print("Create database:", file_path)

def write_data(file_path, word, line_in_file):
    con = sqlite3.connect(file_path)

    cur = con.cursor()
    cur.execute('INSERT INTO parsed_file (id, word, line_in_file) VALUES(NULL, "' + word + '", "' + str(line_in_file) + '")')
    con.commit()
    #print(cur.lastrowid)

def show_data_in_db(file_path):
    con = sqlite3.connect(file_path)

    cur = con.cursor()
    cur.execute('SELECT * FROM parsed_file')
    print(cur.fetchall())
    con.close()

def create_db(file_path):
    con = sqlite3.connect(file_path)

    cur = con.cursor()
    cur.execute('CREATE TABLE parsed_file (id INTEGER PRIMARY KEY, word VARCHAR(100), line_in_file VARCHAR(30))')
    con.commit()
    con.close()

    #write_data(file_path)

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
                if not equal_file:
                    word_list.append(word)

    f.close()

def calc_words_count(file_path):
    global word_list
    word_list = sorted(word_list)
    i = 0
    words_count = {}
    #init words_count
    for element in word_list:
        words_count[word_list[i]] = 1
        i += 1

    #work with file again
    i = 0
    while i < len(words_count):
        scan_file_again(i,file_path)
        i += 1

def scan_file_again(m,file_path):
    f = open(file_path, 'r', encoding='utf8')
    line_number = 0
    for line in f:
        line_number += 1
        target_line = re.findall(word_list[m], line)
        if target_line:
            #print (target_line)
            #print("Word:",word_list[m], " - number in line", len(target_line), "number of line", line_number)
            #print(file_path + ".db")
            write_data(file_path + ".db", word_list[m], line_number)
    f.close()


print_files_on_dir("CSV") #files in dir
file_number = int(input())
copy_rules_from_file(str(files[file_number]))

check_db_exist(str(files[file_number]))
calc_words_count(str(files[file_number]))
show_data_in_db(str(files[file_number]) + ".db")