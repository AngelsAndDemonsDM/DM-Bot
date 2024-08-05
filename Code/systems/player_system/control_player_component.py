from systems.entity_system import BaseComponent

class ControlPlayerComponent(BaseComponent):
    __slots__ = []
    
    def __init__(self) -> None:
        super().__init__('ControlPlayerComponent')

