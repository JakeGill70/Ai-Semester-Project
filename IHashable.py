from abc import ABC, abstractmethod, ABCMeta
from argparse import ArgumentError
import hashlib
import random

from IJsonable import IJsonable

class IHashable(IJsonable, metaclass=ABCMeta):
    
    def getHash(self) -> str:
        return hashlib.md5(self.getJSON().encode()).hexdigest()