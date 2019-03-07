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


def write_data(file_path, list_sql, table):
    con = sqlite3.connect(file_path)
    cur = con.cursor()
    for element in list_sql:
        if table == 'parsed_file':
            word = re.sub(r'\s.*$', '', element)
            line_in_file = re.sub(r'^.*\s', '', element)
            cur.execute('INSERT INTO parsed_file (id, word, line_in_file) VALUES(NULL, "' + word + '", "' + str(line_in_file) + '")')
        elif table == 'phrases':
            element = re.sub(r'\n', '', element)
            cur.execute('INSERT INTO phrases (id, phrase) VALUES(NULL, "' + element + '")')
    con.commit()
    con.close()


def show_data_in_db(file_path, table):
    con = sqlite3.connect(file_path)

    cur = con.cursor()
    cur.execute('SELECT * FROM ' + table)
    print(cur.fetchall())
    con.close()


def create_db(file_path):
    con = sqlite3.connect(file_path)

    cur = con.cursor()
    cur.execute('CREATE TABLE parsed_file (id INTEGER PRIMARY KEY, word VARCHAR(100), line_in_file VARCHAR(30))')
    cur.execute('CREATE TABLE phrases (id INTEGER PRIMARY KEY, phrase VARCHAR(255))')
    con.commit()
    con.close()


def print_files_on_dir(text):
    n = 0   
    print('')
    print('')
    print('===List of files===')
    print('')
    print('')
    while n < len(files):
        name_of_file = files[n]
        result_string = "[" + str(n) + "]" + " - " + name_of_file
        print (result_string)
        n += 1
    print('')
    print('')
    print('===================')
    print('')
    final_message = "Select " + text + " with tests. Enter the number:"
    print(final_message)


def copy_rules_from_file(file_path):
    f = open(file_path, 'r', encoding='utf8')
    list_for_sql = []

    for line in f:
        list_for_sql.append(line)
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
    write_data(file_path + ".db", list_for_sql, "phrases")


def calc_words_count(file_path):
    global word_list
    list_for_sql = []
    word_list = sorted(word_list)

    #work with file again
    i = 0
    while i < len(word_list):
        out_sql_element = scan_file_again(i,file_path)
        for element in out_sql_element:
            list_for_sql.append(element)
        i += 1
    write_data(file_path + ".db", list_for_sql, "parsed_file")


def scan_file_again(m, file_path):
    f = open(file_path, 'r', encoding='utf8')
    line_number = 0
    word_in_lines = []
    for line in f:
        line_number += 1
        target_line = re.findall(word_list[m], line)
        if target_line:
            summing_str = word_list[m] + " " + str(line_number)
            word_in_lines.append(summing_str)
    f.close()
    return word_in_lines


print_files_on_dir("CSV") #files in dir
file_number = int(input())

check_db_exist(str(files[file_number]))
copy_rules_from_file(str(files[file_number]))

calc_words_count(str(files[file_number]))
show_data_in_db(str(files[file_number]) + ".db", "parsed_file")
show_data_in_db(str(files[file_number]) + ".db", "phrases")