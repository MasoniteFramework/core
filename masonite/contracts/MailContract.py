""" Mail Contract """
from abc import ABC, abstractmethod


class MailContract(ABC):
    """ Class for Mail Contract """

    @abstractmethod
    def to(self):
        pass

    @abstractmethod
    def template(self):
        pass

    @abstractmethod
    def send_from(self):
        pass

    @abstractmethod
    def subject(self):
        pass
