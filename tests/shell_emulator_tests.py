import io
import sys
import unittest
import os
import zipfile
import configparser
import task1.shell_emulator as vcl


class TestShellEmulator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        config_data = '''<?xml version="1.0" encoding="UTF-8"?>
        <configuration>
            <Settings>
                <computer_name>test_user</computer_name>
                <fs_zip>virtual_fs_test.zip</fs_zip>
                <log_file>test_log.csv</log_file>
                <startup_script>startup_commands.txt</startup_script>
            </Settings>
        </configuration>'''

        with open('config_test.xml', 'w') as file:
            file.write(config_data)

    @classmethod
    def tearDownClass(cls):
        os.remove('config_test.xml')
        os.remove('virtual_fs_test.zip')
        os.remove('test_log.csv')

    @classmethod
    def setUp(self):
        with zipfile.ZipFile('virtual_fs_test.zip', 'w') as zf:
            zf.writestr('test_directory/file1.txt', 'Test file 1 content')
            zf.writestr('test_directory/file2.txt', 'Test\nTest')
            zf.writestr('test_directory/subdir1/', '')
            zf.writestr('test_directory/subdir1/file3.txt', 'Test file 3 content\nTest file 3 content')
            zf.writestr('test_directory/subdir2/', '')

    def test_load_config(self):
        self.setUp()
        vc = vcl.ShellEmulator('config_test.xml')

        self.assertEqual(vc.computer_name, 'test_user')
        self.assertEqual(vc.fs_zip, 'virtual_fs_test.zip')
        self.assertEqual(vc.log_file, 'test_log.csv')

    # LS
    def test_ls_command(self):
        self.setUp()
        vc = vcl.ShellEmulator('config_test.xml')
        vc.current_dir = 'test_directory/'

        captured_output = io.StringIO()
        sys.stdout = captured_output
        vc.ls(vc.current_dir)
        sys.stdout = sys.__stdout__

        output = captured_output.getvalue().strip().split('\n')
        expected_output = ['file1.txt', 'file2.txt', 'subdir1', 'subdir2']
        self.assertEqual(output, expected_output)

    def test_ls_subdirectory(self):
        self.setUp()
        vc = vcl.ShellEmulator('config_test.xml')
        vc.current_dir = 'test_directory/subdir1/'

        captured_output = io.StringIO()
        sys.stdout = captured_output
        vc.ls(vc.current_dir)
        sys.stdout = sys.__stdout__

        output = captured_output.getvalue().strip().split('\n')
        expected_output = ['file3.txt']
        self.assertEqual(output, expected_output)

    def test_ls_empty(self):
        self.setUp()
        vc = vcl.ShellEmulator('config_test.xml')
        vc.current_dir = 'test_directory/subdir2/'

        captured_output = io.StringIO()
        sys.stdout = captured_output
        vc.ls(vc.current_dir)
        sys.stdout = sys.__stdout__

        output = captured_output.getvalue().strip().split('\n')
        expected_output = ['']
        self.assertEqual(output, expected_output)

# CD
    def test_cd_to_subdirectory(self):
        self.setUp()
        vc = vcl.ShellEmulator('config_test.xml')
        vc.current_dir = 'test_directory/'
        vc.cd(['subdir1'])
        self.assertEqual(vc.current_dir, 'test_directory/subdir1/')

    def test_cd_back_to_parent(self):
        self.setUp()
        vc = vcl.ShellEmulator('config_test.xml')
        vc.current_dir = 'test_directory/subdir1/'
        vc.cd(['..'])
        self.assertEqual(vc.current_dir, 'test_directory/')

    def test_cd_error(self):
        self.setUp()
        vc = vcl.ShellEmulator('config_test.xml')
        vc.current_dir = 'test_directory/'

        captured_output = io.StringIO()
        sys.stdout = captured_output
        vc.cd(['file1.txt'])
        sys.stdout = sys.__stdout__
        output = captured_output.getvalue().strip().split('\n')

        expected_output = ['No such directory: file1.txt']
        self.assertEqual(output, expected_output)

    #UNIQ
    def test_uniq_singlefile(self):
        self.setUp()
        vc = vcl.ShellEmulator('config_test.xml')
        vc.current_dir = 'test_directory/'

        captured_output = io.StringIO()
        sys.stdout = captured_output
        vc.uniq(['file1.txt'])
        sys.stdout = sys.__stdout__

        output = captured_output.getvalue().strip().split('\n')
        self.assertEqual(['Test file 1 content'], output)

    def test_uniq_filewithdoublewords(self):
        self.setUp()
        vc = vcl.ShellEmulator('config_test.xml')
        vc.current_dir = 'test_directory/'

        captured_output = io.StringIO()
        sys.stdout = captured_output
        vc.uniq(['file2.txt'])
        sys.stdout = sys.__stdout__

        output = captured_output.getvalue().strip().split('\n')
        self.assertEqual(['Test'], output)

    def test_uniq_filewithdoublestr(self):
        self.setUp()
        vc = vcl.ShellEmulator('config_test.xml')
        vc.current_dir = 'test_directory/subdir1/'

        captured_output = io.StringIO()
        sys.stdout = captured_output
        vc.uniq(['file3.txt'])
        sys.stdout = sys.__stdout__

        output = captured_output.getvalue().strip().split('\n')
        self.assertEqual(['Test file 3 content'], output)

    #CAL
    def test_cal_today(self):
        self.setUp()
        vc = vcl.ShellEmulator('config_test.xml')

        captured_output = io.StringIO()
        sys.stdout = captured_output
        vc.cal()
        sys.stdout = sys.__stdout__

        output = captured_output.getvalue().strip().split('\n')
        self.assertEqual(['November 2024',
                            'Mo Tu We Th Fr Sa Su',
                            '             1  2  3',
                            ' 4  5  6  7  8  9 10',
                            '11 12 13 14 15 16 17',
                            '18 19 20 21 22 23 24',
                            '25 26 27 28 29 30'], output)

    def test_cal_date(self):
        self.setUp()
        vc = vcl.ShellEmulator('config_test.xml')

        captured_output = io.StringIO()
        sys.stdout = captured_output
        vc.cal(2005, 4)
        sys.stdout = sys.__stdout__

        output = captured_output.getvalue().strip().split('\n')
        self.assertEqual(['April 2005',
                                'Mo Tu We Th Fr Sa Su',
                                '             1  2  3',
                                ' 4  5  6  7  8  9 10',
                                '11 12 13 14 15 16 17',
                                '18 19 20 21 22 23 24',
                                '25 26 27 28 29 30'], output)

if __name__ == '__main__':
    unittest.main()