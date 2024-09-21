import tkinter as tk
import zipfile
import argparse

class VShellGUI:
    def __init__(self, root, fileSystem, username):
        self.root = root
        self.root.title("VShell")
        self.fileSystem = fileSystem
        self.current_directory = "/"
        self.username = username

        # Открытие zip-архива
        with zipfile.ZipFile(self.fileSystem, "r") as zipSystem:
            self.namelist = zipSystem.namelist()

        # множество папок, расположенных в корне файловой системы
        folders_in_main = {
            elem[: elem.find('/') + 1]
            for elem in self.namelist
            if elem.count('/') > 0
        }
        for elem in folders_in_main:
            self.namelist.append(elem)

        self.namedict = dict()
        for path in self.namelist:
            path = path.split('/')
            root = self.namedict
            for elem in path:
                if elem in root:
                    root = root[elem]
                else:
                    root[elem] = dict()
                    root = root[elem]

        # Создание GUI компонентов
        self.command_entry = tk.Entry(self.root, width=50)
        self.command_entry.grid(row=0, column=0, padx=10, pady=10)
        self.command_entry.bind("<Return>", self.process_command)

        self.output_text = tk.Text(self.root, wrap=tk.WORD, width=80, height=20)
        self.output_text.grid(row=1, column=0, padx=10, pady=10)

        # Кнопка для запуска тестов
        self.test_button = tk.Button(self.root, text="Run Tests", command=self.run_tests)
        self.test_button.grid(row=2, column=0, padx=10, pady=10)

    def process_command(self, event):
        """
        Обрабатывает пользовательские команды для работы с VShell.
        - Метод обрабатывает следующие типы команд:
            - "cd": Перемещение между директориями в виртуальной файловой системе.
            - "pwd": Вывод текущей рабочей директории.
            - "ls": Вывод списка файлов и директорий в текущей директории.
            - "rmdir":  Удаление пустых директорий (папок).
            - "head": Вывод первых 10-ти строк содержимого файла.

        - Для завершения работы пользователь может ввести команду "exit".
        - Если введена пустая команда, будет вызвано исключение "No command".
        - Если введена неизвестная команда, будет выведено сообщение "unknown command".
        """
        command = self.command_entry.get().strip()
        self.output_text.insert(tk.END, f"{self.username}:~{self.current_directory}$ {command}\n")

        if len(command) == 0:
            self.output_text.insert(tk.END, f"No command\n")
        elif command == "exit":
            self.root.quit()
        elif command.split()[0] == "cd":
            self.change_directory(command)
        elif command.split()[0] == "pwd":
            self.print_working_directory()
        elif command.split()[0] == "ls":
            self.list_files(command)
        elif command.split()[0] == "rmdir":
            self.remove_directory(command)
        elif command.split()[0] == "head":
            self.head(command)
        else:
            self.output_text.insert(tk.END, f"{command}: unknown command\n")

        self.command_entry.delete(0, tk.END)

    def change_directory(self, command):
        """
        Изменяет текущую рабочую директорию.
            - Если команда содержит ".", то будет выведена текущая директория.
            - Если команда содержит "..", текущая директория будет изменена на родительскую директорию (если возможно).
            - Если команда содержит относительный путь, то он будет преобразован в абсолютный, учитывая текущую директорию.
            - Если указанный путь существует в файловой системе, текущая директория будет изменена на этот путь.
            - В случае, если указанный путь не существует, будет выведено сообщение об ошибке.
        """
        directory = self.normal_split(command)

        if directory == '.':
            return

        if directory == "..":
            if self.current_directory.count('/') > 1:
                self.current_directory = self.current_directory[:self.current_directory.rfind('/')]
            else:
                self.current_directory = '/'
        else:
            if directory[0] != '/':
                directory = f'{self.current_directory}/{directory}' if self.current_directory != '/' else f'/{directory}'

            if f'{directory[1:]}/' in self.namelist:
                self.current_directory = directory
            else:
                self.output_text.insert(tk.END, f"Error: unknown catalog\n")

    def print_working_directory(self):
        """
        Выводит путь к рабочей директории.
            - Игнорирует аргументы.
        """
        self.output_text.insert(tk.END, f"{self.fileSystem.split('.')[0]}{self.current_directory}\n")

    def list_files(self, command):
        """
        Метод выводит список файлов и директорий в указанной или текущей директории в виртуальной файловой системе.
            - Если команда содержит путь к целевой директории, метод выведет содержимое этой директории.
            - Если команда не содержит пути, будет выведено содержимое текущей директории.
         """
        directory = self.current_directory if command.count(' ') == 0 else command.split()[1]

        if self.current_directory == '/':
            if directory == '/':
                pass
            else:
                if not directory.startswith('/'):
                    directory = f'/{directory}'

        if directory[0] != '/':
            directory = f'{self.current_directory}/{directory}'

        path = directory.split('/')[1:] if directory != '/' else []
        cur_dict = self.namedict
        try:
            for item in path:
                cur_dict = cur_dict[item]
            ans = list(sorted(cur_dict.keys())[1:]) if self.namedict != cur_dict else list(cur_dict.keys())
            ans = ' '.join(ans)
            self.output_text.insert(tk.END, f"{ans}\n")
        except Exception:
            self.output_text.insert(tk.END, f"Error: unknown catalog\n")

    def remove_directory(self, command):
        """
        Удаляет директорию из виртуальной файловой системы.
        """
        directory = command.split(' ', 1)[1] if ' ' in command else command

        # Если путь не абсолютный, добавляем текущую директорию
        if not directory.startswith('/'):
            directory = f"{self.current_directory}/{directory}"

        directory = directory.replace('//', '/').lstrip('/').rstrip('/')

        # Проверяем, существует ли такой путь в файловой системе
        if any(d.rstrip('/') == directory for d in self.namelist):
            if directory.endswith('.txt'):
                self.output_text.insert(tk.END, f"Error: {directory} is not a directory\n")
            elif not any(f.startswith(f"{directory}/") for f in self.namelist if f.rstrip('/') != directory):
                self.namelist = [d for d in self.namelist if d.rstrip('/') != directory]
                self.output_text.insert(tk.END, f"Directory /{directory} removed\n")
            else:
                self.output_text.insert(tk.END, f"Error: Directory /{directory} is not empty\n")
        else:
            self.output_text.insert(tk.END, f"Error: Directory /{directory} does not exist\n")

    def head(self, command):
        """
        Вывод первых 10 строк указанного файла в виртуальной файловой системе.
            - Путь к файлу может быть абсолютным (начинается с '/') или относительным.
        """
        file_path = self.normal_split(command)

        if file_path == '0':
            self.output_text.insert(tk.END, f"Error: incorrect input\n")
            return

        # Проверяем, является ли путь относительным, если да - добавляем текущую директорию
        if file_path[0] != '/':
            file_path = f'{self.current_directory}/{file_path}' if self.current_directory != '/' else f'/{file_path}'

        # Проверяем, существует ли файл в архиве
        if file_path[1:] in self.namelist:
            with zipfile.ZipFile(self.fileSystem, "r") as zipSystem:
                with zipSystem.open(file_path[1:]) as file:
                    for i, line in enumerate(file):
                        if i >= 10:
                            break
                        # Выводим только первые 10 строк
                        self.output_text.insert(tk.END, f"{line.decode('UTF-8').strip()}\n")
        else:
            self.output_text.insert(tk.END, f"Error: File {file_path} does not exist\n")

    def normal_split(self, line):
        """
        Разделяет строки на аргументы команды и возвращает последний аргумент.
           - Функция разделяет строку на аргументы, используя пробел в качестве разделителя.
           - Если строка не содержит пробелов, функция возвращает строку "0".
        """
        return '0' if (line.count(' ') == 0) else line[line.rfind(' ') + 1:]

    def make_set(self, namelist):
        """
        Cоздает множество уникальных имен корневых директорий на основе списка имен файлов и директорий.
            -Функция анализирует каждое имя в списке и разделяет его на части, используя символ '/' в качестве разделителя.
            -Затем функция формирует множество, содержащее уникальные имена корневых директорий.
        """
        return {name.split('/')[0] for name in namelist}

    def run_tests(self):
        self.output_text.insert(tk.END, "Running tests...\n")
        self.test_cd()

    def test_cd(self):
        # CD LS
        self.output_text.insert(tk.END, "Current working directory: \n")
        self.list_files("ls")
        self.output_text.insert(tk.END, "Change working directory: \n")

        self.change_directory("cd test_filesystem")
        self.list_files("ls")

        self.change_directory("cd folder")
        self.list_files("ls")

        self.change_directory("cd ..")

        # HEAD
        self.head("head text.txt")
        self.change_directory("cd ..")
        self.head("head test_filesystem/folder/text2.txt")
        self.head("head text3.txt")

        self.change_directory("cd test_filesystem")

        # RMDIR
        self.remove_directory("rmdir folder2")
        self.remove_directory("rmdir folder3")
        self.remove_directory("rmdir folder")


def parse_arguments():
    parser = argparse.ArgumentParser(description="Virtual Shell")
    parser.add_argument("fileSystem", type=str, help="path to the filesystem archive (zip)")
    parser.add_argument("username", type=str, help="username")
    return parser.parse_args()


def main():
    args = parse_arguments()

    if args.fileSystem.split('.')[-1] != 'zip':
        raise ValueError("Filesystem format not supported")

    root = tk.Tk()
    vshell_gui = VShellGUI(root, args.fileSystem, args.username)
    root.mainloop()


if __name__ == "__main__":
    main()
