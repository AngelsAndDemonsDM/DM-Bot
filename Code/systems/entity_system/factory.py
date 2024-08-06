import importlib
import importlib.util
import logging
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

import yaml
from root_path import ROOT_PATH
from systems.entity_system.base_component import BaseComponent
from systems.entity_system.base_entity import BaseEntity
from systems.misc import GlobalClass

logger = logging.getLogger("Entity Factory")

class EntityFactory(GlobalClass):
    __slots__ = [ '_initialized', '_entity_registry', '_component_registry', '_entities', '_uid_dict', '_next_uid' ]

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self._entity_registry: Dict[str, Type[BaseEntity]] = {}
            self._component_registry: Dict[str, Type[BaseComponent]] = {}
            self._entities: Dict[str, BaseEntity] = {}
            self._uid_dict: Dict[int, BaseEntity] = {}
            self._next_uid: int = 1
            
            self._register_classes()
            self.load_entities_from_directory(Path(ROOT_PATH) / "Prototype")

    def _register_classes(self) -> None:
        """Регистрация классов сущностей и компонентов из файлов в директориях."""
        self._auto_register_from_directory(Path(ROOT_PATH) / "Code" / "systems", 'Entity')
        self._auto_register_from_directory(Path(ROOT_PATH) / "Code" / "systems", 'Component')

    def _auto_register_from_directory(self, directory: Path, suffix: str) -> None:
        """Автоматическая регистрация классов из указанной директории.

        Args:
            directory (Path): Директория для сканирования.
            suffix (str): Суффикс для фильтрации классов.
        """
        for file_path in directory.rglob("*.py"):
            module_name = file_path.stem
            if module_name == "__init__":
                continue

            module = self._import_module_from_file(module_name, file_path)
            for name in dir(module):
                cls = getattr(module, name)
                if isinstance(cls, type) and name.endswith(suffix) and not self._is_base_class(cls, suffix):
                    if suffix == 'Entity' and issubclass(cls, BaseEntity):
                        if name not in self._entity_registry:
                            logger.info(f"Registering entity class '{cls.__name__}'")
                            self._entity_registry[name] = cls
                    
                    elif suffix == 'Component' and issubclass(cls, BaseComponent):
                        if name not in self._component_registry:
                            logger.info(f"Registering component class '{cls.__name__}'")
                            self._component_registry[name] = cls

    def _is_base_class(self, cls, suffix: str) -> bool:
        """Проверка, является ли класс базовым.

        Args:
            cls: Класс для проверки.
            suffix (str): Суффикс для фильтрации классов.

        Returns:
            bool: True, если класс является базовым, иначе False.
        """
        if suffix == 'Entity':
            return cls is BaseEntity
        elif suffix == 'Component':
            return cls is BaseComponent
        return False

    def _import_module_from_file(self, module_name, file_path):
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def _create_entity(self, entity_data: Dict[str, Any]) -> BaseEntity:
        """Создание сущности по данным из словаря.

        Args:
            entity_data (Dict[str, Any]): Данные сущности.

        Raises:
            ValueError: Если тип сущности неизвестен или найден дубликат ID.

        Returns:
            BaseEntity: Созданная сущность.
        """
        entity_type = entity_data['type']
        entity_class = self._entity_registry.get(entity_type)
        if not entity_class:
            raise ValueError(f"Unknown entity type: {entity_type}")

        entity_id = entity_data['id']
        key = f"{entity_type}_{entity_id}"

        if key in self._entities:
            raise ValueError(f"Duplicate id {entity_id} for entity type {entity_type}")

        entity = entity_class()
        entity.id = entity_id

        for component_data in entity_data['components']:
            component = self._create_component(component_data)
            entity.add_component(component)

        self._entities[key] = entity
        return entity

    def _create_component(self, component_data: Dict[str, Any]) -> BaseComponent:
        """Создание компонента по данным из словаря.

        Args:
            component_data (Dict[str, Any]): Данные компонента.

        Raises:
            ValueError: Если тип компонента неизвестен.
            TypeError: Если тип данных не соответствует ожидаемому.

        Returns:
            BaseComponent: Созданный компонент.
        """
        from systems.map_system.coordinate import Coordinate

        component_type = component_data.pop('type')
        component_class = self._component_registry.get(component_type)
        if not component_class:
            raise ValueError(f"Unknown component type: {component_type}")

        type_hints = component_class.get_type_hints()
        for key, expected_type in type_hints.items():
            if key == 'coordinates':
                component_data[key] = [Coordinate.from_dict(coord) for coord in component_data[key]]

            if key in component_data and not isinstance(component_data[key], expected_type):
                raise TypeError(f"Expected {key} to be {expected_type} but got {type(component_data[key])}")

        return component_class(**component_data)

    def load_entities_from_yaml(self, file_path: Path) -> List[BaseEntity]:
        """Загрузка сущностей из YAML файла.

        Args:
            file_path (Path): Путь к YAML файлу.

        Returns:
            List[BaseEntity]: Список загруженных сущностей.
        """
        with file_path.open('r', encoding="UTF-8") as file:
            data = yaml.safe_load(file)

        return [self._create_entity(entity_data) for entity_data in data]

    def load_entities_from_directory(self, directory_path: Path) -> None:
        """Загрузка сущностей из всех YAML файлов в директории.

        Args:
            directory_path (Path): Путь к директории.
        """
        self._entities.clear()
        for file_path in directory_path.rglob("*.yml"):
            self._entities.update({f"{entity.type}_{entity.id}": entity for entity in self.load_entities_from_yaml(file_path)})

    def _generate_uid(self) -> int:
        """Генерация уникального идентификатора (UID).

        Returns:
            int: Сгенерированный UID.
        """
        uid = self._next_uid
        self._next_uid += 1
        return uid

    def get_entity_by_id(self, entity_type: str, entity_id: str) -> Optional[BaseEntity]:
        """Получение сущности по типу и ID.

        Args:
            entity_type (str): Тип сущности.
            entity_id (str): ID сущности.

        Returns:
            Optional[BaseEntity]: Сущность, если найдена, иначе None.
        """
        key = f"{entity_type}_{entity_id}"
        if key in self._entities:
            copy_entity = deepcopy(self._entities[key])
            copy_entity.uid = self._generate_uid()
            self._uid_dict[copy_entity.uid] = copy_entity
            return copy_entity
        
        return None

    def get_entity_by_uid(self, uid: int) -> Optional[BaseEntity]:
        """Получение сущности по UID.

        Args:
            uid (int): UID сущности.

        Returns:
            Optional[BaseEntity]: Сущность, если найдена, иначе None.
        """
        return self._uid_dict.get(uid, None)

    def update_object_uid(self, obj: BaseEntity) -> None:
        """Метод для перерегестрации объекта.
        Необходимо для корректной загрузки карты, чтобы не было мёртвых душ

        Args:
            obj (BaseEntity): Объект для перерегестрации
        """
        if self._uid_dict.get(obj.uid) is obj:
            return
        
        obj.uid = self._generate_uid()
        self._uid_dict[obj.uid] = obj
