import os
import zipfile
import csv
from datetime import datetime
import calendar
import xml.etree.ElementTree as ET


class ShellEmulator:
    def __init__(self, config_path):
        self.load_config(config_path)
        self.current_dir = 'virtual_fs/'  # Начальный путь в архиве
        self.init_log()

    def load_config(self, config_path):
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        tree = ET.parse(config_path)
        root = tree.getroot()

        settings = root.find('Settings')
        if settings is None:
            raise KeyError("Missing <Settings> section in the configuration file.")

        required_keys = ['computer_name', 'fs_zip', 'log_file', 'startup_script']
        for key in required_keys:
            element = settings.find(key)
            if element is None:
                raise KeyError(f"Missing key '{key}' in <Settings> section.")
            setattr(self, key, element.text)

        if not zipfile.is_zipfile(self.fs_zip):
            raise FileNotFoundError(f"Invalid zip archive: {self.fs_zip}")

        self.zip = zipfile.ZipFile(self.fs_zip, 'r')

    def init_log(self):
        with open(self.log_file, 'w', newline='') as log:
            writer = csv.writer(log)
            writer.writerow(['Timestamp', 'Command', 'Result'])

    def log(self, command, result):
        with open(self.log_file, 'a', newline='') as log:
            writer = csv.writer(log)
            writer.writerow([datetime.now().isoformat(), command, result])

    def run(self):
        while True:
            command = input(f"{self.computer_name}:{self.current_dir}$ ").strip()
            if command:
                self.handle_command(command)

    def execute_startup_script(self):
        if os.path.exists(self.startup_script):
            with open(self.startup_script, 'r') as script:
                for command in script.readlines():
                    self.handle_command(command.strip())
    def handle_command(self, command):
        parts = command.split()
        cmd = parts[0]
        args = parts[1:]

        if cmd == 'exit':
            self.log(command, 'Exit')
            exit(0)
        elif cmd == 'ls':
            if len(parts)>1:
                self.ls(args[0])
            else:
                self.ls(self.current_dir)
        elif cmd == 'cd':
            self.cd(args)
        elif cmd == 'uniq':
            self.uniq(args)
        elif cmd == 'cal':
            if len(parts)>2:
                self.cal(int(args[0]), int(args[1]))
            else:
                self.cal()
        else:
            print(f"Unknown command: {cmd}")
            self.log(command, 'Unknown command')

    def ls(self, args):
        try:
            items = {name[len(args):].split('/')[0] for name in self.zip.namelist() if name.startswith(args.lstrip('/'))}
            for item in sorted(items):
                if item != '':
                    print(item)
            self.log('ls', 'Success')
        except Exception as e:
            print(f"Error: {e}")
            self.log('ls', f'Error: {e}')

    def cd(self, args):
        if not args:
            print("Usage: cd <directory>")
            return

        target = args[0]
        if target == "..":
            # Переход в родительский каталог
            if self.current_dir != "/":
                self.current_dir = os.path.dirname(self.current_dir.rstrip('/')) + '/'
            self.log(f'cd {target}', 'Success')
            return

        # Новый путь
        new_path = os.path.normpath(os.path.join(self.current_dir, target)).replace("\\","/").lstrip('/')

        # Проверка наличия каталога
        directories = {name.split('/')[0] for name in self.zip.namelist() if name.startswith(new_path + '/')}
        if directories:
            self.current_dir = new_path + '/'
            self.log(f'cd {target}', 'Success')
        else:
            print(f"No such directory: {target}")
            self.log(f'cd {target}', 'Error: No such directory')

    def uniq(self, args):
        if not args:
            print("Usage: uniq <file>")
            return

        file_path = os.path.normpath(os.path.join(self.current_dir, args[0])).replace("\\","/").lstrip('/')
        try:
            with self.zip.open(file_path) as file:
                lines = file.read().decode().splitlines()
                unique_lines = list(dict.fromkeys(lines))
                for el in unique_lines:
                    print(el)
                self.log(f'uniq {args[0]}', 'Success')
        except KeyError:
            print(f"No such file: {args[0]}")
            self.log(f'uniq {args[0]}', 'Error: No such file')
        except Exception as e:
            print(f"Error: {e}")
            self.log(f'uniq {args[0]}', f'Error: {e}')

    def cal(self, year=datetime.now().year, month=datetime.now().month):
        try:
            print(calendar.month(year, month))
            self.log('cal', 'Success')
        except Exception as e:
            print(f"Error: {e}")
            self.log('cal', f'Error: {e}')


if __name__ == "__main__":
    config_path = input("Enter path to config file: ").strip()
    emulator = ShellEmulator(config_path)
    emulator.run()
