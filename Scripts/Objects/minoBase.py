import numpy as np

from Utilities import enum

class MinoBase():
    def __init__(self):
        self.matrix = np.full((4, 4), enum.MinoType.NONE)
    
    
