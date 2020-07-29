from typing import List
from tqdm import tqdm
import os
from pathlib import Path

from parth_core.constants import (SPECIAL_CHARACTERS_REPLACEMENTS_FOR_DIGITS, SPECIAL_CHARACTERS_REPLACEMENTS, \
                                  SPECIAL_END_CHARACTERS, SPECIAL_NUMBERS)


class SeclistGenerator:
    """Generate a list of password based on wordlist provided by user"""

    def __init__(self, word_list, write_enable):
        self.__word_list: List[str] = word_list
        self.__secrets = []
        self.__word = ''
        self.__db = dict()
        self.__write_enable = write_enable

    def generate(self) -> List:
        for word in self.__word_list:
            self.__generate_one_word_secrets(word)
        self.__generate_two_words_secrets()
        self.__generate_three_words_secrets()

        print('Generated {} secrets'.format(len(self.__secrets)))
        if self.__write_enable == 'true':
            self.__write_to_file(self.__secrets)

        return self.__secrets

    def __generate_one_word_secrets(self, word):
        self.__word = word
        self.__secrets = []
        self.__db[word] = {}
        self.__generate_word_forms(word)
        self.__replace_with_special_chars()
        self.__append_connectors()
        self.__append_numbers()

    def __generate_word_forms(self, word):
        word_forms = []
        if not word.isdigit():
            word_forms.extend([word.upper(), word.title(), word.lower()])
        else:
            word_forms.append(word)

        self.__secrets.extend(word_forms)

    def __replace_with_special_chars(self):
        words_with_special_chars = []

        for secret in self.__secrets:
            if secret.isdigit():
                for digit in SPECIAL_CHARACTERS_REPLACEMENTS_FOR_DIGITS:
                    if secret.__contains__(digit):
                        for special_char in SPECIAL_CHARACTERS_REPLACEMENTS_FOR_DIGITS[digit]:
                            output = secret.replace(digit, special_char)
                            words_with_special_chars.append(output)

            for digit in SPECIAL_CHARACTERS_REPLACEMENTS:
                if secret.__contains__(digit):
                    output = secret.replace(digit, SPECIAL_CHARACTERS_REPLACEMENTS[digit])
                    if not words_with_special_chars.__contains__(output):
                        words_with_special_chars.append(output)

        # self.__db[self.__word]['special_chars'] = words_with_special_chars
        self.__secrets.extend(words_with_special_chars)

    def __append_connectors(self):
        words_with_connectors = []
        for key in self.__secrets:
            for char in SPECIAL_END_CHARACTERS:
                output = key + char
                words_with_connectors.append(output)

        # self.__db[self.__word]['connectors'] = words_with_connectors
        self.__db[self.__word]['connectors'] = words_with_connectors
        self.__secrets.extend(words_with_connectors)

    def __append_numbers(self):
        words_ending_with_numbers = []
        for key in self.__db[self.__word]['connectors']:
            for number in SPECIAL_NUMBERS:
                output = key + number
                words_ending_with_numbers.append(output)
        # self.__db[self.__word]['numbers'] = words_ending_with_numbers
        self.__secrets.extend(words_ending_with_numbers)
        self.__db[self.__word]['secrets'] = self.__secrets

    def __generate_two_words_secrets(self):
        all_two_words_password = []
        if len(self.__word_list) > 1:
            for i in range(0, len(self.__word_list)):
                for j in range(0, len(self.__word_list)):
                    if i != j:
                        index = self.__word_list[i]
                        next = self.__word_list[j]
                        index_connectors = self.__db[index]['connectors']
                        next_passwords = self.__db[next]['secrets']
                        temp_passwords = [(first + second).rstrip() for first in index_connectors
                                          for second in next_passwords]
                        all_two_words_password.extend(temp_passwords)

        self.__db['two_words'] = all_two_words_password
        self.__secrets.extend(all_two_words_password)

    def __generate_three_words_secrets(self):
        all_three_words_password = []
        if len(self.__word_list) > 2:
            temp_passwords = [password for password in self.__db['two_words']]
            for temp_password in temp_passwords:
                for input_key in self.__word_list:
                    for entry in self.__db[input_key]['connectors']:
                        three_word_password = (entry+temp_password).rstrip()
                        all_three_words_password.append(three_word_password)

            all_three_words_password.extend(temp_passwords)
        self.__db['three_words'] = all_three_words_password
        self.__secrets.extend(all_three_words_password)

    def __write_to_file(self, passwords):
        parth_directory = os.path.join(str(Path.home()), '.parth')
        if not os.path.exists(parth_directory):
            os.mkdir(parth_directory)
        file_path = os.path.join(parth_directory, 'secret-list.txt')
        if os.path.exists(file_path):
            os.remove(file_path)
        with open(file_path, 'a') as file:
            for password in passwords:
                file.write(password + '\n')

        print('Seclist file path: {}'.format(file_path))