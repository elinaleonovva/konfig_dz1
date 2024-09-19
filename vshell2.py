import tkinter as tk
import zipfile
import argparse
import os

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

        folders_in_main = {
            elem[: elem.find('/') + 1]
            for elem in self.namelist
            if elem.count('/') > 0
        }
        for elem in folders_in_main:
            self.namelist.append(elem)

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

    def run_tests(self):
        self.output_text.insert(tk.END, "Running tests...\n")
        self.test_cd()

    def test_cd(self):
        self.output_text.insert(tk.END, "Current working directory: \n")
        self.list_files("ls")
        self.output_text.insert(tk.END, "Change working directory: \n")

        self.change_directory("cd test_filesystem")
        self.list_files("ls")

        self.change_directory("cd folder")
        self.list_files("ls")

        self.change_directory("cd ..")

        self.head("head text.txt")
        self.change_directory("cd ..")
        self.head("head test_filesystem/folder/text2.txt")
        self.head("head text3.txt")

        self.change_directory("cd test_filesystem")

        self.remove_directory("rmdir folder2")
        self.remove_directory("rmdir folder3")
        self.remove_directory("rmdir folder")

    def change_directory(self, command):
        directory = self.normal_split(command)
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
                directory = f'{self.current_directory}/{directory}' if self.current_directory != '/' else f'/{directory}'

            if f'{directory[1:]}/' in self.namelist:
                self.current_directory = directory
            else:
                self.output_text.insert(tk.END, f"Error: unknown catalog\n")

    def print_working_directory(self):
        self.output_text.insert(tk.END, f"{self.fileSystem.split('.')[0]}{self.current_directory}\n")

    def list_files(self, command):
        directory = self.current_directory if command.count(' ') == 0 else command.split()[1]

        if directory == '/':
            for name in self.make_set(self.namelist):
                self.output_text.insert(tk.END, f"{name}\n")
        else:
            num_of_trans = directory.count('/')
            files_set = {file.split('/')[num_of_trans] for file in self.namelist if directory[1:] in file}
            for elem in files_set:
                if elem != '':
                    self.output_text.insert(tk.END, f"{elem}\n")

    def remove_directory(self, command):
        directory = command.split(' ', 1)[1] if ' ' in command else command

        if not directory.startswith('/'):
            directory = f"{self.current_directory}/{directory}/"

        directory = directory.replace('//', '/').lstrip('/').rstrip('/') + '/'

        if directory in self.namelist:
            if not any(f.startswith(directory) for f in self.namelist if f != directory):
                self.namelist.remove(directory)
                self.output_text.insert(tk.END, f"Directory {directory} removed\n")
            else:
                self.output_text.insert(tk.END, f"Error: Directory {directory} is not empty\n")
        else:
            self.output_text.insert(tk.END, f"Error: Directory {directory} does not exist\n")

    def head(self, command):
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
        return '0' if (line.count(' ') == 0) else line[line.rfind(' ') + 1:]

    def make_set(self, namelist):
        return {name.split('/')[0] for name in namelist}


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
