import unittest

from kdoorweb.db import DB


class TestDB(unittest.TestCase):
    def test_create_db_in_memory(self):
        DB.create_db(dbfile=":memory:")


if __name__ == '__main__':
    unittest.main()
