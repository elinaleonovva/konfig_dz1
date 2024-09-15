import argparse
import contextlib
import os
import zipfile
import unittest


def clearing_comm_beg(command):
    """
    Удаляет пробельные символы с начала строки команды.

    :param command: Строка команды.
    :return: Строка команды без пробельных символов в начале.
    """
    for i in range(len(command) - 1):
        if command[i + 1] != ' ':
            return command[i + 1:]


def clearing_comm_end(command):
    """
    Удаляет пробельные символы с конца строки команды.

    :param command: Строка команды.
    :return: Строка команды без пробельных символов с конца.
    """
    for i in range(len(command), 1, -1):
        if command[i - 1] != ' ':
            return command[:i]


def normal_split(line):
    """
    Разделяет строки на аргументы команды и возвращает последний аргумент.

    - Функция разделяет строку на аргументы, используя пробел в качестве разделителя.
    - Если строка не содержит пробелов, функция возвращает строку "0".

    :param line: Строка команды.
    :return: Последний аргумент команды после разделения по пробелам.
    """
    return '0' if (line.count(' ') == 0) else line[line.rfind(' ') + 1:]


def make_set(namelist):
    """
    Cоздает множество уникальных имен корневых директорий на основе списка имен файлов и директорий.

    Функция анализирует каждое имя в списке и разделяет его на части, используя символ '/' в качестве разделителя.
    Затем функция формирует множество, содержащее уникальные имена корневых директорий.

    :param namelist: Список имен файлов и директорий в виртуальной файловой системе.
    :return: Множество уникальных имен корневых директорий.
    """
    return {name.split('/')[0] for name in namelist}


class VShell:
    """
    Класс для работы с виртуальной файловой системой. Эмулирует работу командной строки.
    """

    def __init__(self, fileSystem):
        """
        Метод выполняет инициализацию объекта, который предназначен для работы с виртуальной файловой системой,
        представленной в виде архива, принимает в качестве аргумента путь к архиву,
        инициализирует текущую рабочую директорию как корневую,
        получает список файлов и директорий, содержащихся внутри архива, и сохраняет их в self.namelist.
        :param fileSystem: путь к файловой системе в запакованном виде
        """
        self.fileSystem = fileSystem  # Сохраняет путь к zip-архиву в атрибуте fileSystem
        self.current_directory = "/"
        #  Открытие zip-фрхива для чтения
        with zipfile.ZipFile(self.fileSystem, "r") as zipSystem:
            self.namelist = zipSystem.namelist()  # Получение списка всех файлов и директорий
        # множество уникальных путей к директориям в корневом уровне архива
        folders_in_main = {
            elem[: elem.find('/') + 1]
            for elem in self.namelist
            if elem.count('/') > 0
        }
        for elem in folders_in_main:
            self.namelist.append(elem)

    def run(self):
        """
                Обрабатывает пользовательские команды для работы с VShell.
                - Метод обрабатывает следующие типы команд:
                    - "cd": Перемещение между директориями в виртуальной файловой системе.
                    - "pwd": Вывод текущей рабочей директории.
                    - "ls": Вывод списка файлов и директорий в текущей директории.
                    - "cat": Вывод содержимого файла.
                    - "--script": Запуск команд из скрипта (необходимо передать путь к скрипту вместе с командой).

                - Для завершения работы пользователь может ввести команду "exit".
                - Если введена пустая команда, будет вызвано исключение "No command".
                - Если введена неизвестная команда, будет выведено сообщение "unknown command".
        """
        while True:
            command = input(f"{self.current_directory}$ ").strip()
            try:
                if len(command) == 0:
                    raise Exception("No command")
                if command == "exit":
                    break
                elif command.split()[0] == "cd":
                    self.change_directory(command)
                elif command.split()[0] == "pwd":
                    self.print_working_directory()
                elif command.split()[0] == "ls":
                    self.list_files(command)
                elif command.split()[0] == "cat":
                    self.read_file(command)
                elif command.split()[0] == "rmdir":
                    self.remove_directory(command)
                elif command.split()[0] == "head":
                    self.head(command)
                else:
                    print(f"{command}: unknown command")
            except Exception as ex:
                print(ex)

    def change_directory(self, command):
        """
        Изменяет текущую рабочую директорию в виртуальной файловой системе.
        - Путь к целевой директории может быть абсолютным (начинается с '/') или относительным.
        - Если команда содержит "0", то текущая директория будет установлена в корневую директорию ("/").
        - Если команда содержит "..", текущая директория будет изменена на родительскую директорию (если возможно).
        - Если команда содержит относительный путь, то он будет преобразован в абсолютный, учитывая текущую директорию.
        - Если указанный путь существует в файловой системе, текущая директория будет изменена на этот путь.
        - В случае, если указанный путь не существует, будет выведено сообщение об ошибке.
        :param command: путь к новой рабочей директории
        """
        directory = normal_split(command)

        if directory == '0':
            self.current_directory = '/'
            return

        if directory == "..":
            if self.current_directory.count('/') > 1:
                self.current_directory = self.current_directory[:self.current_directory.rfind('/')]
            else:
                self.current_directory = '/'
        else:
            if directory[0] != '/':
                if self.current_directory != '/':
                    directory = f'{self.current_directory}/{directory}'
                else:
                    directory = f'/{directory}'

            if f'{directory[1:]}/' in self.namelist:
                self.current_directory = directory
                return

            print("Error: unknown catalog")

    def print_working_directory(self):
        """
        Выводит путь к рабочей директории в виртуальной файловой системе.
        """
        print(self.fileSystem.split('.')[0] + self.current_directory)

    def list_files(self, command):
        """
        Метод list_files выводит список файлов и директорий в указанной или текущей директории
        в виртуальной файловой системе.

        - Метод выводит список файлов и директорий в указанной или текущей директории в виртуальной файловой системе.
        - Если команда содержит путь к целевой директории, метод выведет содержимое этой директории.
        - Если команда не содержит пути, будет выведено содержимое текущей директории.
        :param command: Путь к директории, содержимое которой нужно вывести. Может быть пустым.
        """
        if command.count(' ') > 0:
            directory = normal_split(command)

            if directory[0] != '/':
                if self.current_directory != '/':
                    directory = f'{self.current_directory}/{directory}'  # путь к директории корректируется относительно текущей рабочей директории
                else:
                    directory = f'/{directory}'

            if f'{directory[1:]}/' not in self.namelist:
                print("Error: unknown directory")
                return

        else:
            directory = self.current_directory

        if directory == '/':
            for name in make_set(self.namelist):
                print(name)
        #  создаётся множество файлов в указанной директории
        else:
            num_of_trans = directory.count('/')
            files_set = {
                file.split('/')[num_of_trans]
                for file in self.namelist
                if (directory[1:] in file)
            }
            for elem in files_set:
                if elem != '':
                    print(elem)

    def read_file(self, command):
        """
        Читает содержимое указанного файла в виртуальной файловой системе.

        - Путь к файлу может быть абсолютным (начинается с '/') или относительным.
        - Если указанный файл существует, его содержимое будет выведено на экран.
        - Если файл не существует, будет выведено сообщение об ошибке.

        :param command: Строка команды, которая содержит имя файла для чтения.
        """
        file_path = normal_split(command)

        if file_path == '0':
            print("Error: incorrect input")
            return

        if file_path[0] != '/':
            if self.current_directory != '/':
                file_path = f'{self.current_directory}/{file_path}'
            else:
                file_path = f'/{file_path}'

        # Проверка, существует ли указанный файл в списке файлов и директорий self.namelist
        if file_path[1:] in self.namelist:
            with zipfile.ZipFile(self.fileSystem, "r") as zipSystem:
                with zipSystem.open(file_path[1:], "r") as file:
                    read_file = file.read()
            print(read_file.decode('UTF-8'))

            return

        print("Error: unknown file")

    def remove_directory(self, command):
        """
        Удаляет директорию из виртуальной файловой системы.
        """
        command = command.strip()
        directory = command.split(' ', 1)[1] if ' ' in command else command

        # Формируем абсолютный путь, если это относительный путь
        if not directory.startswith('/'):
            directory = f"{self.current_directory}/{directory}/"

        # Нормализуем путь (убираем дублирующиеся слэши)
        directory = directory.replace('//', '/')

        # Проверим путь без завершающего слэша, так как директории могут храниться без него
        directory = directory.lstrip('/').rstrip('/') + '/'

        if directory in self.namelist:
            if not any(f.startswith(directory) for f in self.namelist if f != directory):
                self.namelist.remove(directory)
                print(f"Directory {directory} removed")
            else:
                print(f"Error: Directory {directory} is not empty")
        else:
            print(f"Error: Directory {directory} does not exist")

    def head(self, command):
        """
        Вывод первых 10 строк указанного файла в виртуальной файловой системе.

        - Путь к файлу может быть абсолютным (начинается с '/') или относительным.
        :param command: Строка команды, которая содержит путь к файлу.
        """
        file_path = normal_split(command)
        if file_path[0] != '/':
            if self.current_directory != '/':
                file_path = f'{self.current_directory}/{file_path}'
            else:
                file_path = f'/{file_path}'
        # проверка существует ли файл в списке файлов и директорий в виртуальной файловой системе
        if file_path[1:] in self.namelist:
            with zipfile.ZipFile(self.fileSystem, "r") as zipSystem:  # открывает zip-архив с файловой системой
                with zipSystem.open(file_path[1:], "r") as file:
                    for i, line in enumerate(file):
                        if i >= 10:
                            break
                        print(line.decode('UTF-8').strip())
        else:
            print(f"Error: File {file_path} does not exist")


def test_ls(vshell):
    vshell.list_files("")


def test_cd(vshell):
    print("Current working directory: ")
    vshell.list_files("ls")
    print("Change working directory: ")
    vshell.list_files("ls")
    vshell.head("head test_filesystem/folder/text2.txt")


if __name__ == "__main__":
    # unittest.main()
    vshell = VShell("test_filesystem.zip")
    # test_cd(vshell)
    vshell.run()
