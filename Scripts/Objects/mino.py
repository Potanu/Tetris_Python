from Utilities import define
from Utilities import enum

class Mino():
    def __init__(self, mino_type):
        self.index = 0
        self.mino_type = mino_type
        self.set_mino()
    
    def set_mino(self):
        match self.mino_type:
            case enum.MinoType.I:
                self.matrix = define.MINO_I_MATRIX
            case enum.MinoType.O:
                self.matrix = define.MINO_O_MATRIX
            case enum.MinoType.S:
                self.matrix = define.MINO_S_MATRIX
            case enum.MinoType.Z:
                self.matrix = define.MINO_Z_MATRIX
            case enum.MinoType.J:
                self.matrix = define.MINO_J_MATRIX
            case enum.MinoType.L:
                self.matrix = define.MINO_L_MATRIX
            case enum.MinoType.T:
                self.matrix = define.MINO_T_MATRIX

    def rotate_right(self):
        self.index = 0 if len(self.matrix) <= self.index + 1 else \
            self.clamp(self.index + 1, 0, len(self.matrix) - 1)
    
    def rotate_left(self):
         self.index = len(self.matrix) - 1 if self.index == 0 else \
             self.clamp(self.index - 1, 0, len(self.matrix) - 1)
    
    # どこかに汎用的なメソッドとしてまとめた方が良いかもしれない
    def clamp(self, value, min_num, max_num):
        return max(min_num, min(value, max_num))
