from abc import ABC, abstractmethod
from argparse import ArgumentError
import hashlib
import random

class IJsonable():

    @abstractmethod
    def getJSON(self) -> str:
        pass