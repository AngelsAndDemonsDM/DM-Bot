from typing import Dict, List

from systems.entity_system import BaseEntity
from systems.misc import GlobalClass
from systems.player_system.control_player_component import \
    ControlPlayerComponent


class PlayerManager(GlobalClass):
    __slots__ = ['_initialized', '_player_dict']
    
    def __init__(self) -> None:
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self._player_dict: Dict[str, List[BaseEntity]] = {}

    def register_entitys(self, entitys: List[BaseEntity]):
        entitys = list(entitys)
        
        for entity in entitys:
            comp = entity.get_component('ControlPlayerComponent')
            if comp:
                login = comp.login
                if login not in self._player_dict:
                    self._player_dict[login] = []
                
                self._player_dict[login].append(entity)

    def add_player_entity(self, login: str, entity: BaseEntity) -> None:
        if login not in self._player_dict:
            self._player_dict[login] = []
        
        self._player_dict[login].append(entity)
        entity.add_component(ControlPlayerComponent(login))

    def remove_player_entity(self, login: str, uid: int) -> None:
        if login in self._player_dict:
            new_player_entities = []
            for entity in self._player_dict[login]:
                if entity.uid != uid:
                    new_player_entities.append(entity)
                
                else:
                    entity.remove_component("ControlPlayerComponent")
            
            self._player_dict[login] = new_player_entities

    def get_player_entitys(self, login: str) -> List[BaseEntity]:
        pass
