from abc import ABC, abstractmethod

class SceneBase(ABC):
    @abstractmethod
    def update(self):
        pass
    
    @abstractmethod
    def draw(self):
        pass
