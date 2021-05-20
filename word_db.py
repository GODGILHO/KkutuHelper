import re

unknown_checker = re.compile('.\?.*')


class DB:
    def __init__(self, filename):
        self.file = open(filename, 'r')
        self.datas = self.file.readlines()
        self.clear_data = []
        for value in self.datas:
            if unknown_checker.match(value):
                continue
            self.clear_data.append(value)

    def get_longest_of(self, start_char: str or list, exception_list=None):
        if exception_list is None:
            exception_list = []
        if type(start_char) == str:
            checker = [re.compile('{}.*'.format(start_char))]
        elif type(start_char) == list:
            checker = [re.compile('{}.*'.format(start_char[0])), re.compile('{}.*'.format(start_char[1]))]
        current = ''
        for value in self.clear_data:
            if value in exception_list:
                continue
            if checker[0].match(value):
                if current == '':
                    current = value
                else:
                    if len(value) > len(current):
                        current = value
            if len(checker) == 2:
                if checker[1].match(value):
                    if current == '':
                        current = value
                    else:
                        if len(value) > len(current):
                            current = value
        return current.rstrip()
