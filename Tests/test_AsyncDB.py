import unittest
import asyncio
import os
import aiosqlite
from Code.db_work import AsyncDB, DBF_PRIMARY_KEY, DBF_UNIQUE, DBF_AUTOINCREMENT, DBF_NOT_NULL

class TestAsyncDB(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.db_name = "test_db"
        self.db_path = "test_path"
        self.db_config = {
            'departments': [
                ('id', int, DBF_PRIMARY_KEY | DBF_AUTOINCREMENT, None),
                ('name', str, DBF_NOT_NULL, None)
            ],
            'employees': [
                ('id', int, DBF_PRIMARY_KEY | DBF_AUTOINCREMENT, None),
                ('name', str, DBF_NOT_NULL, None),
                ('age', int, DBF_NOT_NULL, None),
                ('email', str, DBF_UNIQUE, None),
                ('department_id', int, DBF_NOT_NULL, 'departments.id')
            ]
        }
        self.db = AsyncDB(self.db_name, self.db_path, self.db_config)
        await self.db.open()

    async def asyncTearDown(self):
        await self.db.close()
        if os.path.exists(self.db._db_path):
            os.remove(self.db._db_path)
        # Завершаем все оставшиеся задачи
        tasks = [task for task in asyncio.all_tasks() if task is not asyncio.current_task()]
        for task in tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

    async def test_insert_and_select(self):
        await self.db.insert('departments', {'name': 'HR'})
        result = await self.db.select('departments')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['name'], 'HR')

    async def test_update(self):
        await self.db.insert('departments', {'name': 'HR'})
        await self.db.update('departments', {'name': 'Human Resources'}, "name = 'HR'")
        result = await self.db.select('departments')
        self.assertEqual(result[0]['name'], 'Human Resources')

    async def test_delete(self):
        await self.db.insert('departments', {'name': 'HR'})
        await self.db.delete('departments', "name = 'HR'")
        result = await self.db.select('departments')
        self.assertEqual(len(result), 0)

if __name__ == '__main__':
    unittest.main()
