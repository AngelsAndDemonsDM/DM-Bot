import asyncio
import importlib.util
import logging
import re
from inspect import signature
from pathlib import Path
from typing import Any, Callable, Dict, List

from root_path import ROOT_PATH
from systems.misc import GlobalClass

logger = logging.getLogger("Event manager")


class EventManager(GlobalClass):
    __slots__ = ['_open_events', '_protected_events', '_initialized']
    
    def __init__(self) -> None:
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self._open_events: Dict[str, List[Callable[..., Any]]] = {}
            self._protected_events: Dict[str, List[Callable[..., Any]]] = {}
            
            self._register_events()

    @staticmethod
    def _import_module_from_file(module_name, file_path):
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def _register_event(self, event_dict: Dict[str, List[Callable[..., Any]]], event_name: str, func: Callable[..., Any]) -> None:
        if event_name not in event_dict:
            event_dict[event_name] = []
        
        event_dict[event_name].append(func)

    def _register_events(self) -> None:
        event_name_pattern = re.compile(r"^(?:o_|p_)?(.+?)_event$") 

        events_directory = Path(ROOT_PATH) / "Code" / "systems"
        for file_path in events_directory.rglob("*.py"):
            module_name = file_path.stem  # Имя модуля без расширения .py
            if module_name == "__init__":
                continue # Иначе будет регестрация по 15 раз одного и того же
            
            module = self._import_module_from_file(module_name, file_path)

            for name in dir(module):
                handler = getattr(module, name)
                if callable(handler):
                    match = event_name_pattern.match(name)
                    if match:
                        event_name = match.group(1)  # Извлекаем имя события без модификаторов и суффиксов
                        if name.startswith("o_"):
                            self._register_event(self._open_events, event_name, handler)
                            logger.info(f"Registered open event '{event_name}' with handler '{handler.__name__}'")
                        
                        elif name.startswith("p_"):
                            self._register_event(self._protected_events, event_name, handler)
                            logger.info(f"Registered protected event '{event_name}' with handler '{handler.__name__}'")

    def register_open_event(self, event_name: str, func: Callable[..., Any]) -> None:
        self._register_event(self._open_events, event_name, func)

    def register_protected_event(self, event_name: str, func: Callable[..., Any]) -> None:
        self._register_event(self._protected_events, event_name, func)

    async def _call_event(self, event_dict: Dict[str, List[Callable[..., Any]]], event_name: str, *args, **kwargs) -> None:
        handlers = event_dict.get(event_name, [])
        for handler in handlers:
            handler_signature = signature(handler)
            handler_kwargs = {k: v for k, v in kwargs.items() if k in handler_signature.parameters}
            if asyncio.iscoroutinefunction(handler):
                await handler(*args, **handler_kwargs)
            else:
                handler(*args, **handler_kwargs)

    async def call_open_event(self, event_name: str, *args, **kwargs) -> None:
        await self._call_event(self._open_events, event_name, *args, **kwargs)

    async def call_protected_event(self, event_name: str, *args, **kwargs) -> None:
        await self._call_event(self._protected_events, event_name, *args, **kwargs)

    async def call_all_event(self, event_name: str, *args, **kwargs) -> None:
        await self._call_event(self._open_events, event_name, *args, **kwargs)
        await self._call_event(self._protected_events, event_name, *args, **kwargs)
