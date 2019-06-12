"""Dev Command."""
import os
import shutil
import subprocess

from cleo import Command


class DevCommand(Command):
    """
    Run dev commands

    dev
        {location=None : Location of file/directory to test or lint}
        {--t|--test : Run Pytest on file or directory}
        {--l|--lint : Run Flake8 on file or directory}
    """

    def handle(self):
        
        # Run pytest
        if self.option("test"):
            location = self.argument("location").lower() if self.argument("location") != "None" else "."
            subprocess.call(["python3 -m pytest {location} -v --color=yes".format(location=location)], shell=True)

        # Run Flake8
        if self.option("lint"):
            location = self.argument("location").lower() if self.argument("location") != "None" else "masonite/"
            subprocess.call(["flake8 {location} --ignore=E501,F401,E128,E402,E731,F821,E712,W503".format(location=location)], shell=True)

        # Command did nothing
        if not self.option("test") and not self.option("lint"):
            print("No actions selected")
