"""Tests for update_wiki.py"""

import os
import sqlite3
import unittest
from unittest.mock import Mock, MagicMock

import update_wiki

try:
    os.remove("sql/db/test_update_wiki.sql")
except FileNotFoundError:
    pass
db_wiki = sqlite3.connect("sql/db/test_update_wiki.sql")
with open("sql/functions/init_db.sql") as f:
    db_wiki.executescript(f.read())
with open("sql/functions/populate_test_db.sql") as f:
    db_wiki.executescript(f.read())
db_wiki.commit()
db_wiki.close()

class TestWiki(unittest.TestCase):

    def test_update(self):
        reddit = MagicMock()
        subreddit = "test_wiki+foo"
        after_epoch = 0

        reddit.user.me.return_value = "groupbot"

        update_wiki.update(reddit, subreddit, after_epoch)
        reddit.subreddit().wiki.__getitem__().edit.assert_called_once()
