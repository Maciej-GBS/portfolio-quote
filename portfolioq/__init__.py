from abc import abstractmethod
import numpy as np
import pandas as pd

class IPerformance:
    @abstractmethod
    def get_transactions(self):
        pass

class IDividends:
    pass
