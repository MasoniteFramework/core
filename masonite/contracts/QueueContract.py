""" Queue Contract """
from abc import ABC, abstractmethod


class QueueContract(ABC):
    """ Class for Queue Contract """

    @abstractmethod
    def push(self):
        pass
