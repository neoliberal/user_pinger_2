"""Remove deleted/suspended/inactive accounts as well as dead groups"""

# TODO check if groups are inactive and make hidden

import os
import sqlite3
import sys
import time

import praw
import prawcore

import slack_python_logging


# TODO put in environment variables
logger = slack_python_logging.getLogger(
    app_name = "user_pinger-prune",
    slack_loglevel = "CRITICAL",
    stream_loglevel = "DEBUG"
)

# Log uncaught exceptions to Slack before exiting
def log_excepthook(ex_type, ex_value, ex_traceback):
    logger.critical(
        "Critical Exception caught, exiting",
        exc_info=(ex_type, ex_value, ex_traceback)
    )
sys.excepthook = log_excepthook  # Wish I could use a lambda :pensive:

subreddit = os.environ["SUBREDDIT"]
db = sqlite3.connect(f"sql/db/{subreddit}.db")
reddit = praw.Reddit(
    client_id=os.environ["CLIENT_ID"],
    client_secret=os.environ["CLIENT_SECRET"],
    refresh_token=os.environ["REFRESH_TOKEN"],
    user_agent="linux:user_pinger_2-prune:v0.0.1 (by /u/jenbanim)"
)

with db:
    with open("sql/functions/get_all_subscribers.sql") as f:
        subscribers = [x[0] for x in db.execute(f.read()).fetchall()]

subscribers = ["unidan"]

for user in subscribers:
    # TODO figure out this part
    #
    # I wrote a whole thing here trying to get people's karma and use the
    # reponse from Reddit to determine whether they were deleted or suspended.
    # But alas, the Reddit API sucks too much ass, and I could not. Turns out
    # best way to determine whether a user is deleted or suspended is to try to
    # send that user a message, so I need to put that logic into `bot.py`.
    #
    # Therefore, I presume, this section shall heretoforth be used for the
    # detection and removal of inactive accounts exclusively.
