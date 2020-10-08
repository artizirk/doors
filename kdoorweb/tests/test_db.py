import unittest

from kdoorweb.db import DB


class TestDB(unittest.TestCase):
    def setUp(self) -> None:
        self.db = DB()

    def test_create_db_in_memory(self):
        DB.create_db(dbfile=":memory:")

    def test_create_db_in_connection(self):
        DB.create_db(dbfile=self.db)


if __name__ == '__main__':
    unittest.main()
