import re
import os
import sqlite3

directory = '.'
files = os.listdir(directory)

WORD_WEIGHT = 3


class WordsDatabase:
    def __init__(self, input_file):
        self.input_file = input_file
        self.database_file = "{}.db".format(self.input_file)
        self.word_list = []
        self.check_db_exist()

    def check_db_exist(self):
        while True:
            if os.path.isfile(self.database_file):
                print("База данных {} уже существует. Переписать?".format(self.database_file))
                print("(Y)es | (N)o?")

                answer = input()
                pattern_for_yes = '(^[yY]$|^[yY][eE][sS]$|^[дД]$|^[дД][аА]$)'

                if re.match(pattern_for_yes, answer):
                    os.remove(self.database_file)
                    print("Удаляю старую версию базы данных {}".format(self.database_file))
                else:
                    break
            else:
                self.create_db()
                print("Создана база: {}".format(self.database_file))
                self.copy_words_from_file()
                print("Вычисляю уникальные слова и словосочетания...")
                self.calc_words_count()
                # show_data_in_db(db_file_path, "parsed_file")
                # show_data_in_db(db_file_path, "phrases")
                # show_data_in_db(db_file_path, "unique_words")
                break

    def create_db(self):
        con = sqlite3.connect(self.database_file)
        cur = con.cursor()
        cur.execute('CREATE TABLE parsed_file (id INTEGER PRIMARY KEY, word VARCHAR(100), line_in_file VARCHAR(30))')
        cur.execute('CREATE TABLE phrases (id INTEGER PRIMARY KEY, phrase VARCHAR(255))')
        cur.execute('CREATE TABLE unique_words (id INTEGER PRIMARY KEY, word VARCHAR(255), word_count INTEGER)')
        cur.execute('CREATE TABLE word_group (id INTEGER PRIMARY KEY, words VARCHAR(255), word_group_count INTEGER)')
        con.commit()
        con.close()

    def calc_words_count(self):
        list_for_sql = []
        self.word_list = sorted(self.word_list)
        uw_table = UniqueWords(self.database_file, "unique_words")
        uw_table.write_data(self.word_list)

        # work with file again
        for word in self.word_list:
            out_sql_element = self.scan_file_again(self.word_list.index(word))
            for element in out_sql_element:
                list_for_sql.append(element)
        write_data(self.database_file, list_for_sql, "parsed_file")
        self.calc_unique_words()
        self.calc_word_groups()

    def copy_words_from_file(self):
        self._clear_semicolon()
        f = open(self.input_file, 'r', encoding='utf8')
        list_for_sql = []

        for line in f:
            list_for_sql.append(line)
            pattern_re = re.findall(r'.*', line)
            pattern_for_utterance = "".join(pattern_re)
            utterance = pattern_for_utterance.split()
            for word in utterance:
                if len(word) >= WORD_WEIGHT:
                    equal_word = False
                    if word in self.word_list:
                        equal_word = True
                    if not equal_word:
                        self.word_list.append(word)
        f.close()
        write_data(self.database_file, list_for_sql, "phrases")

    def scan_file_again(self, m):
        f = open(self.input_file, 'r', encoding='utf8')
        line_number = 0
        word_in_lines = []
        for line in f:
            line_number += 1
            target_line = re.findall("(\s|^){}(\s|$)".format(self.word_list[m]), line)
            if target_line:
                word_in_lines.append("{} {}".format(self.word_list[m], line_number))
        f.close()
        return word_in_lines

    def calc_unique_words(self):
        con = sqlite3.connect(self.database_file)
        cur = con.cursor()
        for element in self.word_list:
            cur.execute(
                'update unique_words set word_count = ( select count(*) from parsed_file where word = \"{0}\" ) '
                'where word = \"{0}\"'.format(element))
        con.commit()
        con.close()

    def calc_word_groups(self):
        con = sqlite3.connect(self.database_file)
        cur = con.cursor()

        cur.execute('SELECT count(*) FROM phrases')
        max_lines = cur.fetchone()

        for element in range(max_lines[0]):
            cur.execute('SELECT word FROM parsed_file where line_in_file = {}'.format(element + 1))
            elements_for_find = []
            rollover_elements = []

            while True:
                elements = cur.fetchone()

                if not elements:
                    break
                elements_for_find.append(elements[0])

            for unique_word in elements_for_find:
                for again_unique_word in elements_for_find:
                    if not unique_word == again_unique_word:
                        if not (([unique_word, again_unique_word] in rollover_elements) or (
                                [again_unique_word, unique_word] in rollover_elements)):
                            cur.execute('SELECT * FROM word_group where words like \"{}\"'.format(
                                [unique_word, again_unique_word]))
                            if not cur.fetchone():
                                cur.execute(
                                    'INSERT INTO word_group (id, words, word_group_count) VALUES(NULL, \"{}\", NULL)'.format(
                                        [unique_word, again_unique_word]))
                                cur.execute(
                                    'update word_group set word_group_count = ( select count(*) from phrases where {} ) where words = \"{}\"'.format(
                                        summing_words_for_find("phrase", [unique_word, again_unique_word]),
                                        [unique_word, again_unique_word]))
                            rollover_elements.append([unique_word, again_unique_word])
        con.commit()
        con.close()

    def _clear_semicolon(self):
        deleted_semicolon = []
        with open(self.input_file, 'r', encoding='utf8') as f:
            for line in f:
                deleted_semicolon.append(re.sub(r';', '', line))
        with open(self.input_file, 'w', encoding='utf8') as f:
            for element in deleted_semicolon:
                f.write(element)


class UniqueWords:
    def __init__(self, database_file, table_name):
        self.database_file = database_file
        self.table_name = table_name

    def show_data(self):
        con = sqlite3.connect(self.database_file)
        cur = con.cursor()
        cur.execute('SELECT * FROM {} ORDER BY word_count'.format(self.table_name))
        for cur_element in cur.fetchall():
            print("Слово \"{}\" встречается {} раз".format(cur_element[1], cur_element[2]))
        con.close()

    def write_data(self, list_sql):
        con = sqlite3.connect(self.database_file)
        cur = con.cursor()
        for element in list_sql:
            cur.execute('INSERT INTO unique_words (id, word, word_count) VALUES(NULL, \"{}\", NULL)'.format(element))
        con.commit()
        con.close()


def summing_words_for_find(column, words_array):
    resulting_string = ""
    for word in words_array:
        if resulting_string == "":
            resulting_string = resulting_string + "{} like \"%{}%\"".format(column, word)
        else:
            resulting_string = resulting_string + " and {} like \"%{}%\"".format(column, word)
    return resulting_string


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
    con.commit()
    con.close()


def show_data_in_db(file_path, table):
    con = sqlite3.connect(file_path)

    cur = con.cursor()
    cur.execute('SELECT * FROM {}'.format(table))
    print(cur.fetchall())
    con.close()


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


def print_files_on_dir(text):
    print('\n===List of files===')
    for file in files:
        print("[{}] - {}".format(files.index(file), file))
    print('===================\n')
    final_message = "Select {} with tests. Enter the number:".format(text)
    print(final_message)


def input_words():
    print("Введите через пробел слова для поиска:")
    keywords = input()
    return keywords.split()


print_files_on_dir("CSV") #files in dir
file_number = int(input())

csv_file_path = str(files[file_number])
words_db = WordsDatabase(csv_file_path)

while True:
    words = input_words()
    find_phrases_by_words(words_db.database_file, "phrases", "phrase", words)
