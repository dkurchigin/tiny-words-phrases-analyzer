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

    return file_path

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
        elif table == 'unique_words':
            cur.execute('INSERT INTO unique_words (id, word) VALUES(NULL, "' + element + '")')
    con.commit()
    con.close()


def show_data_in_db(file_path, table):
    con = sqlite3.connect(file_path)

    cur = con.cursor()
    cur.execute('SELECT * FROM ' + table)
    print(cur.fetchall())
    #for element in cur.fetchall():
        #print(element[1])
    con.close()


def create_db(file_path):
    con = sqlite3.connect(file_path)

    cur = con.cursor()
    cur.execute('CREATE TABLE parsed_file (id INTEGER PRIMARY KEY, word VARCHAR(100), line_in_file VARCHAR(30))')
    cur.execute('CREATE TABLE phrases (id INTEGER PRIMARY KEY, phrase VARCHAR(255))')
    cur.execute('CREATE TABLE unique_words (id INTEGER PRIMARY KEY, word VARCHAR(255))')
    con.commit()
    con.close()


def print_files_on_dir(text):
    print('\n===List of files===')
    for file in files:
        print("[{}] - {}".format(files.index(file), file))
    print('===================\n')
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
    write_data(file_path + ".db", word_list, "unique_words")

    #work with file again
    for word in word_list:
        out_sql_element = scan_file_again(word_list.index(word),file_path)
        for element in out_sql_element:
            list_for_sql.append(element)
    write_data(file_path + ".db", list_for_sql, "parsed_file")


def scan_file_again(m, file_path):
    f = open(file_path, 'r', encoding='utf8')
    line_number = 0
    word_in_lines = []
    for line in f:
        line_number += 1
        target_line = re.findall(word_list[m], line)
        if target_line:
            word_in_lines.append("{} {}".format(word_list[m], line_number))
    f.close()
    return word_in_lines


def find_phrases_by_words(file_path, table, column, *words):
    con = sqlite3.connect(file_path)

    cur = con.cursor()
    cur.execute('SELECT * FROM ' + table + ' WHERE ' + summing_words_for_find(column, words) + '')
    print(cur.fetchall())
    con.close()


def summing_words_for_find(column, words):
    print(words, "<-")
    resulting_string = ""
    for word in words[0]:
        if resulting_string == "":
            resulting_string = resulting_string + "{} like \"%{}%\"".format(column, word)
        else:
            resulting_string = resulting_string + " and {} like \"%{}%\"".format(column, word)
    return resulting_string


print_files_on_dir("CSV") #files in dir
file_number = int(input())

csv_file_path = str(files[file_number])
db_file_path = check_db_exist(csv_file_path)

copy_rules_from_file(csv_file_path)

calc_words_count(csv_file_path)
show_data_in_db(db_file_path, "parsed_file")
show_data_in_db(db_file_path, "phrases")
show_data_in_db(db_file_path, "unique_words")
words = ["самсунг", "телевизор"]
find_phrases_by_words(db_file_path, "phrases", "phrase", words)
