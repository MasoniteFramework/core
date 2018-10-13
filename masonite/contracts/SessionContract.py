""" Session Contract """
from abc import ABC, abstractmethod


class SessionContract(ABC):
    """ Class for Session Contract """

    @abstractmethod
    def get(self):
        pass

    @abstractmethod
    def set(self):
        pass

    @abstractmethod
    def has(self):
        pass

    @abstractmethod
    def all(self):
        pass

    @abstractmethod
    def delete(self):
        pass

    @abstractmethod
    def flash(self):
        pass

    @abstractmethod
    def reset(self):
        pass

    @abstractmethod
    def helper(self):
        pass
