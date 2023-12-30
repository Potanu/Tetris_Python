from Utilities import enum
from Utilities import pygameManager
from Scenes import sceneBase
from Scenes import sceneManager

class TitleScene(sceneBase.SceneBase):
    def update(self):
        if pygameManager.PygameManager().is_pressed(enum.KeyType.A):
            sceneManager.SceneManager().move_Scene(enum.SceneType.GAME)
        self.draw()
        
    def draw(self):
        # テスト背景
        bg_tuple = (enum.ObjectType.BG, 0, enum.DrawType.FILL, -1, "#0000FF", -1, -1, 1, -1, -1)
        sceneManager.SceneManager().add_draw_queue(bg_tuple)
