from typing import Any, Dict, Type

from systems.entity_system import BaseComponent


class ControlPlayerComponent(BaseComponent):
    __slots__ = []
    
    def __init__(self, login: str) -> None:
        super().__init__('ControlPlayerComponent') 
        self.login: str = login
    
    def __repr__(self) -> str:
        """Возвращает строковое представление компонента.
        Этот метод должен быть переопределен в подклассах, чтобы возвращать строку,
        содержащую имя класса и параметры его конструктора.

        Returns:
            str: Строковое представление компонента.
        """
        return f"ControlPlayerComponent(login={self.login})"

    @staticmethod
    def get_type_hints() -> Dict[str, Type[Any]]:
        """Возвращает словарь с именами переменных и их типами.
        Этот метод должен быть переопределен в подклассах, чтобы возвращать корректные типы
        для каждого атрибута компонента.

        Returns:
            Dict[str, Type[Any]]: Словарь с именами переменных и их типами.
        """
        return {
            'login': str
        }
