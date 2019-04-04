import re
import os
import sqlite3

directory = '.'
files = os.listdir(directory)

word_list = []

WORD_WEIGHT = 3


def check_db_exist(file_path):
    base_extension = ".db"
    file_path = file_path + base_extension

    if os.path.isfile(file_path):
        print("База данных {} уже существует. Переписать?".format(file_path))
        print("(Y)es | (N)o?")

        answer = input()
        pattern_for_yes = '(^[yY]$|^[yY][eE][sS]$|^[дД]$|^[дД][аА]$)'

        if re.match(pattern_for_yes, answer):
            os.remove(file_path)
            print("Удаляю старую версию базы данных {}".format(file_path))
    create_db(file_path)
    print("Создана база: {}".format(file_path))
    return file_path, True


def write_data(file_path, list_sql, table):
    con = sqlite3.connect(file_path)
    cur = con.cursor()
    for element in list_sql:
        if table == 'parsed_file':
            word = re.sub(r'\s.*$', '', element)
            line_in_file = re.sub(r'^.*\s', '', element)
            cur.execute('INSERT INTO parsed_file (id, word, line_in_file) VALUES(NULL, \"{}\", {})'
                        ''.format(word, str(line_in_file)))
        elif table == 'phrases':
            element = re.sub(r'\n', '', element)
            cur.execute('INSERT INTO phrases (id, phrase) VALUES(NULL, \"{}\")'.format(element))
        elif table == 'unique_words':
            cur.execute('INSERT INTO unique_words (id, word, word_count) VALUES(NULL, \"{}\", NULL)'.format(element))
    con.commit()
    con.close()


def calc_unique_words(file_path, list_sql):
    con = sqlite3.connect(file_path)
    cur = con.cursor()
    for element in list_sql:
        cur.execute('update unique_words set word_count = ( select count(*) from parsed_file where word = \"{0}\" ) '
                    'where word = \"{0}\"'.format(element))
    con.commit()
    con.close()

    
def calc_word_groups(file_path):
    con = sqlite3.connect(file_path)
    cur = con.cursor()
    
    cur.execute('SELECT count(*) FROM phrases')
    max_lines = cur.fetchone()
    
    for element in range(max_lines[0]):
        cur.execute('SELECT word FROM parsed_file where line_in_file = {}'.format(element+1))
        elements_for_find = []
        
        while True:
            elements = cur.fetchone()
                
            if elements == None:
                break
            elements_for_find.append(elements[0])
        
        for unique_word in elements_for_find:
            for again_unique_word in elements_for_find:
                if not unique_word == again_unique_word:
                    cur.execute('INSERT INTO word_group (id, words, word_group_count) VALUES(NULL, \"{}\", NULL)'.format([unique_word, again_unique_word]))
                    cur.execute('update word_group set word_group_count = ( select count(*) from phrases where {} ) where words = \"{}\"'.format(summing_words_for_find("phrase", [unique_word, again_unique_word]),[unique_word, again_unique_word]))
    
    con.commit()
    con.close()
    

def show_data_in_db(file_path, table):
    con = sqlite3.connect(file_path)

    cur = con.cursor()
    if table == "unique_words":
        cur.execute('SELECT * FROM {} ORDER BY word_count'.format(table))
        for cur_element in cur.fetchall():
            print("Слово \"{}\" встречается {} раз".format(cur_element[1], cur_element[2]))
    else:
        cur.execute('SELECT * FROM {}'.format(table))
        print(cur.fetchall())
    con.close()


def create_db(file_path):
    con = sqlite3.connect(file_path)

    cur = con.cursor()
    cur.execute('CREATE TABLE parsed_file (id INTEGER PRIMARY KEY, word VARCHAR(100), line_in_file VARCHAR(30))')
    cur.execute('CREATE TABLE phrases (id INTEGER PRIMARY KEY, phrase VARCHAR(255))')
    cur.execute('CREATE TABLE unique_words (id INTEGER PRIMARY KEY, word VARCHAR(255), word_count INTEGER)')
    cur.execute('CREATE TABLE word_group (id INTEGER PRIMARY KEY, words VARCHAR(255), word_group_count INTEGER)')
    con.commit()
    con.close()


def print_files_on_dir(text):
    print('\n===List of files===')
    for file in files:
        print("[{}] - {}".format(files.index(file), file))
    print('===================\n')
    final_message = "Select {} with tests. Enter the number:".format(text)
    print(final_message)


def clear_semicolon(file_path):
    deleted_semicolon = []
    with open(file_path, 'r', encoding='utf8') as f:
        for line in f:
            deleted_semicolon.append(re.sub(r';', '', line))
    with open(file_path, 'w', encoding='utf8') as f:
        for element in deleted_semicolon:
            f.write(element)


def copy_rules_from_file(file_path):
    clear_semicolon(file_path)
    f = open(file_path, 'r', encoding='utf8')
    list_for_sql = []

    for line in f:
        list_for_sql.append(line)
        pattern_re = re.findall(r'.*', line)
        pattern_for_utterance = "".join(pattern_re)
        utterance = pattern_for_utterance.split()
        for word in utterance:
            if len(word) >= WORD_WEIGHT:
                equal_word = False
                if word in word_list:
                    equal_word = True
                if not equal_word:
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
        out_sql_element = scan_file_again(word_list.index(word), file_path)
        for element in out_sql_element:
            list_for_sql.append(element)
    write_data(file_path + ".db", list_for_sql, "parsed_file")
    calc_unique_words(file_path + ".db", word_list)
    calc_word_groups(file_path + ".db")


def scan_file_again(m, file_path):
    f = open(file_path, 'r', encoding='utf8')
    line_number = 0
    word_in_lines = []
    for line in f:
        line_number += 1
        target_line = re.findall("(\s|^){}(\s|$)".format(word_list[m]), line)
        if target_line:
            word_in_lines.append("{} {}".format(word_list[m], line_number))
    f.close()
    return word_in_lines


def find_phrases_by_words(file_path, table, column, words_for_find):
    con = sqlite3.connect(file_path)
    cur = con.cursor()
    try:
        cur.execute('SELECT * FROM {} WHERE {}'.format(table, summing_words_for_find(column, words_for_find)))
        print('SELECT * FROM {} WHERE {}'.format(table, summing_words_for_find(column, words_for_find)))
        print(cur.fetchall())
    except sqlite3.OperationalError:
        print("Ошибка ввода, возможно введена пустая строка")
    con.close()


def summing_words_for_find(column, words_array):
    resulting_string = ""
    for word in words_array:
        if resulting_string == "":
            resulting_string = resulting_string + "{} like \"%{}%\"".format(column, word)
        else:
            resulting_string = resulting_string + " and {} like \"%{}%\"".format(column, word)
    return resulting_string


def input_words():
    print("Введите через пробел слова для поиска:")
    keywords = input()
    return keywords.split()


print_files_on_dir("CSV") #files in dir
file_number = int(input())

csv_file_path = str(files[file_number])
db_file_path, write_to_db = check_db_exist(csv_file_path)

if write_to_db:
    copy_rules_from_file(csv_file_path)
    calc_words_count(csv_file_path)

#show_data_in_db(db_file_path, "parsed_file")
#show_data_in_db(db_file_path, "phrases")
#show_data_in_db(db_file_path, "unique_words")
while True:
    words = input_words()
    find_phrases_by_words(db_file_path, "phrases", "phrase", words)
