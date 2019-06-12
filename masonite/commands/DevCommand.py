"""Dev Command."""
import subprocess

from cleo import Command


class DevCommand(Command):
    """
    Run dev commands

    dev
        {location=None : Location of file/directory to test or lint}
        {--t|--test : Run Pytest on file or directory}
        {--l|--lint : Run Flake8 on file or directory}
        {--c|--clean : Clean project. Remove .pyc files and __pycache__/ directories}
    """

    def handle(self):

        # Run pytest
        if self.option('test'):
            location = self.argument('location').lower() if self.argument('location') != 'None' else '.'
            subprocess.call(['python3 -m pytest {location} -v --color=yes'.format(location=location)], shell=True)

        # Run Flake8
        if self.option('lint'):
            location = self.argument('location').lower() if self.argument('location') != 'None' else 'masonite/'
            subprocess.call(['flake8 {location} --ignore=E501,F401,E128,E402,E731,F821,E712,W503'.format(location=location)], shell=True)

        # Clean repo (Works for Windows, MacOS, and Linux)
        if self.option('clean'):
            subprocess.call(["python3", "-c", "import pathlib; [p.unlink() for p in pathlib.Path('.').rglob('*.py[co]')]"])
            subprocess.call(["python3", "-c", "import pathlib; [p.rmdir() for p in pathlib.Path('.').rglob('__pycache__')]"])

        # Command did nothing
        if not self.option('test') and not self.option('lint') and not self.option('clean'):
            self.info('No actions selected')
