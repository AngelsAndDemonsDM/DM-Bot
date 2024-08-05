from typing import Dict, List

from systems.entity_system import BaseEntity
from systems.misc import GlobalClass


class PlayerManager(GlobalClass):
    __slots__ = ['_initialized', '_player_dict']
    
    def __init__(self) -> None:
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self._player_dict: Dict[str, List[BaseEntity]] = {}

    def add_player_entity(self, player: str, obj: BaseEntity) -> None:
        if player not in self._player_dict:
            self._player_dict[player] = []
        
        self._player_dict[player].append(obj) # TODO: Компонент для указания что мы контролируем данный объект

    def remove_player_entity(self, player: str, uid: int) -> None:
        if player in self._player_dict:
            new_player_entities = []
            for entity in self._player_dict[player]:
                if entity.uid != uid:
                    new_player_entities.append(entity)
                
                else:
                    pass  # TODO: Компонент для указания что мы контролируем данный объект
            
            self._player_dict[player] = new_player_entities
