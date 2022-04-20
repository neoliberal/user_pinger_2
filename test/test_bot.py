"""Tests for bot.py"""

import os
import sqlite3
import time
import unittest
from unittest.mock import Mock, ANY

import praw

import bot


try:
    os.remove("sql/db/test_commands.db")
except FileNotFoundError:
    pass
try:
    os.remove("sql/db/test_pings.db")
except FileNotFoundError:
    pass
db_pings = sqlite3.connect("sql/db/test_pings.db")
db_commands = sqlite3.connect("sql/db/test_commands.db")
with open("sql/functions/init_db.sql") as f:
    init_db = f.read()
    db_pings.executescript(init_db)
    db_commands.executescript(init_db)
with open("sql/functions/populate_test_db.sql") as f:
    populate_test_db = f.read()
    db_pings.executescript(populate_test_db)
    db_commands.executescript(populate_test_db)
db_pings.commit()
db_commands.commit()
db_pings.close()
db_commands.close()

class TestBot(unittest.TestCase):

    def test_pings(self):

        reddit = Mock()
        logger = Mock()
        subreddit = Mock()
        comment = Mock()

        comment.banned_by = None
        comment.author = Mock()
        comment.author.__str__ = Mock()
        comment.permalink = "https://www.reddit.com/r/neoliberal/comments/pmnxhh/discussion_thread/hcme2j7/"
        comment.created_utc = time.time()+1 # time travel
        reddit.inbox.unread.return_value = []
        reddit.subreddit.return_value = subreddit
        subreddit.moderator.return_value = ["jenbanim"]
        subreddit.__str__ = Mock()
        subreddit.__str__.return_value = "test_pings"
        os.environ["SUBREDDIT"] = "test_pings"
        subreddit.stream.comments.return_value = [comment]
        user_pinger = bot.UserPinger(reddit, logger)

        # Valid Pings

        comment.author.__str__.return_value = "jenbanim"
        comment.id = "ping_no_alias"
        comment.body = "!ping KITTY"
        user_pinger.listen()
        reddit.redditor.assert_called_once_with("jenbanim-2")
        reddit.redditor.reset_mock()
        comment.reply.assert_called_once()
        comment.reply.reset_mock()

        comment.author.__str__.return_value = "jenbanim"
        comment.id = "ping_multiple"
        comment.body = "!ping KITTY&UKRAINE"
        user_pinger.listen()
        #reddit.redditor.assert_has_calls(["jenbanim-2", "foo"])
        assert 2 == reddit.redditor.call_count
        reddit.redditor.reset_mock()
        comment.reply.assert_called_once()
        comment.reply.reset_mock()

        comment.id = "ping_with_parent"
        comment.body = "!ping KITTY"
        comment.is_root = False
        comment.parent.is_root = True
        comment.parent.permalink = "root_comment_permalink"
        user_pinger.listen()
        reddit.redditor.assert_called_once_with("jenbanim-2")
        reddit.redditor.reset_mock()
        comment.reply.assert_called_once()
        comment.reply.reset_mock()
        # Only test once
        comment.is_root = True

        comment.id = "ping_with_alias"
        comment.body = "!ping CAT"
        user_pinger.listen()
        reddit.redditor.assert_called_once_with("jenbanim-2")
        reddit.redditor.reset_mock()
        comment.reply.assert_called_once()
        comment.reply.reset_mock()

        comment.id = "ping_mod_non-subscriber"
        comment.body = "!ping UKRAINE"
        user_pinger.listen()
        reddit.redditor.assert_called_once_with("foo")
        reddit.redditor.reset_mock()
        comment.reply.assert_called_once()
        comment.reply.reset_mock()

        # Invalid Pings

        comment.author.__str__.return_value = "jenbanim-2"
        comment.id = "ping_non-mod_non-subscriber"
        comment.body = "!ping UKRAINE"
        user_pinger.listen()
        comment.author.message.assert_called_once()
        comment.author.message.reset_mock()
        logger.warning.assert_called_once()
        logger.warning.reset_mock()

        comment.id = "ping_non-mod_locked"
        comment.body = "!ping CONTROVERSIAL"
        user_pinger.listen()
        comment.author.message.assert_called_once()
        comment.author.message.reset_mock()
        logger.warning.assert_called_once()
        logger.warning.reset_mock()

        comment.id = "ping_invalid_group"
        comment.body = "!ping A!@#B"
        user_pinger.listen()
        comment.author.message.assert_called_once()
        comment.author.message.reset_mock()
        logger.warning.assert_called_once()
        logger.warning.reset_mock()

        comment.id = "ping_too_many_pings"
        comment.body = "!ping FOO !ping BAR"
        user_pinger.listen()
        comment.author.message.assert_called_once()
        comment.author.message.reset_mock()
        logger.warning.assert_called_once()
        logger.warning.reset_mock()

        reddit.redditor.assert_not_called()


    def test_commands(self):

        reddit = Mock()
        logger = Mock()
        subreddit = Mock()
        message = Mock()

        message.__class__ = praw.models.Message # I hate this so much
        message.author = Mock()
        message.author.__str__ = Mock()
        message.permalink = "https://www.reddit.com/r/neoliberal/comments/pmnxhh/discussion_thread/hcme2j7/"
        message.created_utc = time.time()+1 # time travel
        reddit.subreddit.return_value = subreddit
        reddit.inbox.unread.return_value = [message]
        subreddit.moderator.return_value = ["jenbanim"]
        subreddit.__str__ = Mock()
        subreddit.__str__.return_value = "test_commands"
        os.environ["SUBREDDIT"] = "test_commands"
        subreddit.stream.comments.return_value = []
        user_pinger = bot.UserPinger(reddit, logger)

        # Invalid commands

        message.author.__str__.return_value = "jenbanim-2"
        message.id = "message_subscribe_protected"
        message.body = "subscribe CONTROVERSIAL"
        user_pinger.listen()
        message.author.message.assert_called_once()
        message.author.message.reset_mock()
        logger.warning.assert_called_once()
        logger.warning.reset_mock()

        message.author.__str__.return_value = "jenbanim"
        message.id = "message_invalid_command"
        message.body = "gain_sentience"
        user_pinger.listen()
        message.author.message.assert_called_once()
        message.author.message.reset_mock()
        logger.warning.assert_called_once()
        logger.warning.reset_mock()

        message.id = "message_subscribe_invalid_group"
        message.body = "subscribe A!!A"
        user_pinger.listen()
        message.author.message.assert_called_once()
        message.author.message.reset_mock()
        logger.warning.assert_called_once()
        logger.warning.reset_mock()

        message.id = "message_subscribe_nonexistent_group"
        message.body = "subscribe SDKJFDSLKJFS"
        user_pinger.listen()
        message.author.message.assert_called_once()
        message.author.message.reset_mock()
        logger.warning.assert_called_once()
        logger.warning.reset_mock()

        # Valid commands

        message.id = "message_subscribe_mod_locked"
        message.body = "subscribe CONTROVERSIAL"
        user_pinger.listen()
        message.author.message.assert_called_once()
        message.author.message.reset_mock()

        message.id = "message_subscribe"
        message.body = "subscribe UKRAINE"
        user_pinger.listen()
        message.author.message.assert_called_once()
        message.author.message.reset_mock()

        message.id = "message_unsubscribe"
        message.body = "unsubscribe UKRAINE"
        user_pinger.listen()
        message.author.message.assert_called_once()
        message.author.message.reset_mock()

        message.id = "message_subscribe_alias"
        message.body = "subscribe CAT"
        user_pinger.listen()
        message.author.message.assert_called_once()
        message.author.message.reset_mock()

        message.id = "message_list_my_subscriptions"
        message.body = "list_my_subscriptions"
        user_pinger.listen()
        message.author.message.assert_called_once()
        message.author.message.reset_mock()

        message.id = "message_unsubscribe_all"
        message.body = "unsubscribe"
        user_pinger.listen()
        message.author.message.assert_called_once()
        message.author.message.reset_mock()

        logger.warning.assert_not_called()
