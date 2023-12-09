from Utilities import define
from Utilities import enum

class Mino():
    def __init__(self, mino_type):
        self.index = 0
        self.left_upper_grid = define.START_MINO_GRID
        self.fall_counter = 0
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
    
    def check_fall(self, fall_speed):
        if fall_speed <= self.fall_counter:
            self.fall_counter = 0
            return True
        else:
            self.fall_counter += 1
            return False
    
    def move_mino(self, move_type):
        match move_type:
            case enum.MinoMoveType.MOVE_RIGHT:
                self.left_upper_grid = (self.left_upper_grid[0] + 1, self.left_upper_grid[1])
            case enum.MinoMoveType.MOVE_LEFT:
                self.left_upper_grid = (self.left_upper_grid[0] - 1, self.left_upper_grid[1])
            case enum.MinoMoveType.ROTATE_RIGHT:
                self.index = self.get_next_index(1)
            case enum.MinoMoveType.ROTATE_LEFT:
                self.index = self.get_next_index(-1)
            case enum.MinoMoveType.FALL:
                self.left_upper_grid = (self.left_upper_grid[0], self.left_upper_grid[1] + 1)
    
    def get_next_index(self, add_num):
        index = self.index + add_num
        if index < 0:
            index = len(self.matrix) - 1
        elif len(self.matrix) <= index:
            index = 0
        return index
        
    # どこかに汎用的なメソッドとしてまとめた方が良いかもしれない
    def clamp(self, value, min_num, max_num):
        return max(min_num, min(value, max_num))
