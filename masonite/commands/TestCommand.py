""" A Test Command """
from cleo import Command
from subprocess import call


class TestCommand(Command):
    """
    Test Masonite Project

    test
    """

    def handle(self):
        call(["python", "-m", "pytest"])
