import asyncio
import json
import os
from functools import reduce
from typing import Any, Optional

import aiofiles


class SettingsManager:
    __slots__ = ['_path', '_lock']
    
    def __init__(self, settings_name: str = "main_settings") -> None:
        """Инициализирует менеджер настроек.

        Args:
            settings_name (str, optional): Имя файла настроек. Defaults to "main_settings".

        Example:
        ```py
        settings_manager = SettingsManager("app_settings")
        ```
        """
        self._path: str = os.path.join(os.getcwd(), 'data', 'settings', f'{settings_name}.json')
        self._lock = asyncio.Lock()

    async def _create_file(self) -> bool:
        """Создает файл настроек, если он не существует.

        Returns:
            bool: Возвращает True, если файл был создан, иначе False.

        Example:
        ```py
        created = await settings_manager._create_file()
        print(created)  # True, если файл создан, иначе False
        ```
        """
        directory = os.path.dirname(self._path)

        if not os.path.exists(directory):
            os.makedirs(directory)

        if not os.path.exists(self._path):
            async with aiofiles.open(self._path, "w") as file:
                await file.write(json.dumps({}))
            
            return True
            
        return False

    async def _load_settings(self) -> dict:
        """Загружает настройки из файла без использования блокировки.

        Returns:
            dict: Словарь с настройками.
        """
        if not os.path.exists(self._path):
            await self._create_file()

        async with aiofiles.open(self._path, "r") as file:
            content = await file.read()
            settings = json.loads(content)
        
        return settings

    async def _save_settings(self, settings: dict) -> None:
        """Сохраняет настройки в файл без использования блокировки.

        Args:
            settings (dict): Словарь с настройками.

        Example:
        ```py
        await settings_manager._save_settings_unlocked({"theme": "dark", "volume": 75})
        ```
        """
        async with aiofiles.open(self._path, "w") as file:
            await file.write(json.dumps(settings, indent=4))

    async def load_settings(self) -> dict:
        """Загружает настройки из файла.

        Returns:
            dict: Словарь с настройками.

        Example:
        ```py
        settings = await settings_manager.load_settings()
        print(settings)
        ```
        """
        async with self._lock:
            return await self._load_settings()

    async def save_settings(self, settings: dict) -> None:
        """Сохраняет настройки в файл.

        Args:
            settings (dict): Словарь с настройками.

        Example:
        ```py
        await settings_manager.save_settings({"theme": "dark", "volume": 75})
        ```
        """
        async with self._lock:
            await self._save_settings(settings)

    async def set_setting(self, key: str, value: Any) -> None:
        """Устанавливает значение настройки.

        Args:
            key (str): Ключ настройки, поддерживается вложенность через точку (например, "user.preferences.theme").
            value (Any): Значение настройки.

        Example:
        ```py
        await settings_manager.set_setting("user.preferences.theme", "dark")
        ```
        """
        async with self._lock:
            settings = await self._load_settings()
            keys = key.split('.')
            d = settings

            for k in keys[:-1]:
                if k not in d:
                    d[k] = {}
                d = d[k]
            
            d[keys[-1]] = value
            
            await self._save_settings(settings)

    async def get_setting(self, key: str) -> Optional[Any]:
        """Получает значение настройки.

        Args:
            key (str): Ключ настройки, поддерживается вложенность через точку (например, "user.preferences.theme").

        Returns:
            Optional[Any]: Значение настройки или None, если ключ не найден.

        Example:
        ```py
        theme = await settings_manager.get_setting("user.preferences.theme")
        print(theme)  # "dark"
        ```
        """
        async with self._lock:
            settings = await self._load_settings()
            try:
                return reduce(lambda d, k: d[k], key.split('.'), settings)
            
            except KeyError:
                return None
