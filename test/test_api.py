# TODO this file is out of date and only kept here as a reminder

"""Tests for api.py"""

import os
import sqlite3
import unittest

import api


try:
    os.remove("sql/db/test_api.sql")
except FileNotFoundError:
    pass
db_api = sqlite3.connect("sql/db/test_api.sql")
with open("sql/functions/init_db.sql") as f:
    db_api.executescript(f.read())
with open("sql/functions/populate_test_db.sql") as f:
    db_api.executescript(f.read())
db_api.commit()
db_api.close()


class TestAPI(unittest.TestCase):

    def test_list_groups(self):
        username = "jenbanim"
        subreddit = "test_api"
        after_epoch = 0

        print(api.list_groups(username, subreddit, after_epoch))
