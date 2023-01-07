"""Script for running user_pinger bot."""

import os
import time
from typing import Deque
import sqlite3
import string
import sys
import urllib.parse

import praw
import prawcore

import slack_python_logging
import pinglib


class UserPinger:
    """Main Bot Class -- instantiate and call listen() to run"""


    def __init__(self, reddit, logger):
        """Initialize"""
        self.reddit = reddit
        self.username = self.reddit.user.me()
        self.subreddit = self.reddit.subreddit(
            os.environ["SUBREDDIT"]
        )
        self.primary_subreddit = self.reddit.subreddit(
            os.environ["SUBREDDIT"].split("+")[0]
        )
        self.logger = logger
        # Comments should be added to self.parsed immeditately before any
        # non-idempotent actions are taken. This gives us the best chance of
        # recovering from an error on Reddit's side that may resolve on retries
        # while ensuring we never message someone twice
        self.parsed = Deque(maxlen=1000)
        self.start_time = time.time()
        # Create our DB connection and initialize the database if empty
        # Keeping the handle open shouldn't impact data correctness
        # The file descriptor should get garbage-collected on exit
        self.db = sqlite3.connect(f"sql/db/{str(self.primary_subreddit)}.db")
        # con.commit() is called automatically this way
        with self.db:
            with open("sql/functions/init_db.sql") as f:
                self.db.executescript(f.read())
        self.logger.info("Initialized")


    def listen(self):
        """Main bot function. Monitors for pings and commands"""
        # Investigate double-ping bug on metaNL. Does subreddit.stream.comments
        # ALWAYS return comments in order of newest to oldest even when using a
        # muti-reddit?
        for comment in self.subreddit.stream.comments(pause_after=1):
            if comment is None:
                break # comment stream done, listen to messages
            if not (
                comment.banned_by is not None  # removed or spam filtered
                or comment.created_utc < self.start_time  # prior to startup
                or str(comment) in self.parsed  # already been handled
            ):
                self.handle_comment(comment)
        for item in self.reddit.inbox.unread(limit=1):
            if isinstance(item, praw.models.Message):
                # Only trigger on messages, not replies or username pings
                if item.created_utc > self.start_time:
                    # Only trigger on messages posted after startup
                    self.handle_message(item)
                else:
                    item.mark_read()
            else:
                item.mark_read()


    def ping_error_reply(self, comment, error):
        """Sends an error message

        Includes a link to the comment, documentation, and modmail
        """
        with open("templates/ping_error_message.txt") as f:
            message_template = string.Template(f.read())
        message = message_template.substitute(
            comment_url = comment.permalink,
            error = error,
            primary_subreddit = str(self.primary_subreddit)
        )
        comment.author.message(
            subject="Ping Error",
            message = message
        )


    def handle_comment(self, comment):
        """handles comments"""

        # Get token containing group(s) to be pinged
        self.logger.debug(
            "%s handling comment from user %s", 
            comment.id, 
            str(comment.author)
        )
        comment_split = comment.body.upper().split()
        try:
            index = comment_split.index("!PING")
        except ValueError:
            # no trigger
            self.parsed.append(comment.id)
            return
        # TODO
        # Swtich to regex matching? Could be faster and could easily handle
        # punctuation surrounding !ping, as in [!ping foo](https://bar.com)
        if comment_split.count("!PING") > 1:
            self.logger.warning("%s Too many \"!pings\"", comment.id)
            self.parsed.append(comment.id)
            error = (
                "Only use one \"!ping\" per comment. To ping multiple groups, "
                "concatenate groups with \"&\" eg. \"!ping DOG&KITTY\""
            )
            self.ping_error_reply(comment, error)
            return
        try:
            # token contains ALL groups to be pinged eg. "DOG&KITTY"
            token = comment_split[index + 1]
            # Stripping punctuation handles comments like:
            # "!ping WEEBS, what do you think of this?"
            token = token.strip(string.punctuation)
        except IndexError:
            self.logger.warning("%s Missing group, sending error", comment.id)
            self.parsed.append(comment.id)
            self.ping_error_reply(comment, "Please specify a group to ping")
            return
        self.logger.debug("%s found token %s ", comment.id, token)

        # Validate token and groups therein
        # We concatenate groups with "&" rather than "+" to avoid ambiguity
        # with the hyphens in group names that could be interpreted as a minus
        # sign (eg. USA-WA)
        max_group_pings = 3
        groups = token.split("&")
        if len(groups) > max_group_pings:
            self.logger.warning(
                "%s too many groups, sending error", comment.id
            )
            error = (
                f"The token {token} is invalid. You cannot ping more than "
                f"{max_group_pings} groups at once."
            )
            self.parsed.append(comment.id)
            self.ping_error_reply(comment, error)
            return
        for group in groups:
            if not pinglib.group_name_is_valid(group):
                self.logger.warning(
                    "%s group %s is invalid", comment.id, group
                )
                error = f"The group name {group} is invalid"
                self.parsed.append(comment.id)
                self.ping_error_reply(comment, error)
                return
        self.logger.debug("%s Token and group(s) valid", comment.id)

        # Ensure group(s) exist
        with self.db:
            with open("sql/functions/get_groups_and_aliases.sql") as f:
                db_groups = [
                    group[0] for group in self.db.execute(f.read()).fetchall()
                ]
        for group in groups:
            if group not in db_groups:
                self.logger.warning(
                    "%s group %s does not exist", comment.id, group
                )
                self.parsed.append(comment.id)
                self.ping_error_reply(comment, f"{group} does not exist")
                return
        self.logger.debug("%s Group(s) exist", comment.id)

        # De-alias our group list, ensure no duplicates
        with self.db:
            with open("sql/functions/de-alias.sql") as f:
                de_alias = {
                    item[0]: item[1]
                    for item
                    in self.db.execute(f.read()).fetchall()
                }
        groups = list(set([de_alias[group] for group in groups]))

        # Ensure user has permission to ping group(s)
        mods = self.primary_subreddit.moderator()
        try:
            mods = [mod.name for mod in mods]
        except AttributeError:
            # This allows for passing in mods as a list of strings during tests
            pass
        if str(comment.author) not in mods:
            for group in groups:
                # Check if subscribed
                with self.db:
                    with open("sql/functions/get_group_subscribers.sql") as f:
                        subscribers = [
                            username[0] 
                            for username 
                            in self.db.execute(f.read(), {"group_name": group})
                        ]
                if str(comment.author).lower() not in subscribers:
                    self.logger.warning(
                        "%s not subscribed to %s", comment.id, group
                    )
                    self.parsed.append(comment.id)
                    error = (
                        f"You must subscribe to {group} before you can ping it"
                    )
                    self.ping_error_reply(comment, error)
                    return
                # Check if locked
                with self.db:
                    with open("sql/functions/is_locked.sql") as f:
                        locked = bool(self.db.execute(
                            f.read(), {"group_name": group}
                        ).fetchall()[0][0])
                if locked:
                    self.logger.warning(
                        "%s group %s is locked", comment.id, group
                    )
                    self.parsed.append(comment.id)
                    error = (
                        f"You cannot ping {group} because it has been locked "
                        "by the moderators"
                    )
                    self.ping_error_reply(comment, error)
                    return
        self.logger.debug("%s has permission to ping group(s)", comment.id)

        try:
            reply = comment.reply(f"^(Pinging {token}...)")
        except praw.exceptions.APIException:
            self.logger.warning("%s Ping was deleted, exiting", comment.id)
            return
        self.logger.debug("%s Reply posted", comment.id)

        # Send ping messages
        log_data = {
            "comment_id": comment.id,
            "permalink": comment.permalink,
            "author": str(comment.author).lower(),
            "token": token,
            "created_epoch_sec": int(comment.created_utc)
        }
        with self.db:
            with open("sql/functions/log_ping.sql") as f:
                self.db.execute(f.read(), log_data)
        self.parsed.append(comment.id) # do not attempt retry below this point
        pinged = []
        for group in groups:
            subject = f"Ping in {group} from {str(comment.author)}"
            with open("templates/ping_message.txt") as f:
                message_template = string.Template(f.read())
            message = message_template.substitute(
                bot_username=self.username,
                comment_url=comment.permalink,
                group=token,
                group_encoded=urllib.parse.quote(token)
            )
            with self.db:
                with open("sql/functions/log_ping_group.sql") as f:
                    self.db.execute(
                        f.read(), 
                        {"group_name": group, "comment_id": comment.id}
                    )
                with open("sql/functions/get_group_subscribers.sql") as f:
                    subscribers = [
                        username[0] 
                        for username 
                        in self.db.execute(f.read(), {"group_name": group})
                    ]
            for subscriber in subscribers:
                if subscriber == str(comment.author).lower():
                    # Don't ping the person who sent the ping
                    continue
                if subscriber in pinged:
                    # Don't ping again if we've already pinged them once
                    continue
                try:
                    self.logger.debug("%s pinging %s", subscriber)
                    pinged.append(subscriber)
                    self.reddit.redditor(subscriber).message(
                        subject=subject, message=message
                    )
                except praw.exceptions.APIException as ex:
                    # Don't care why. We'll check for deleted/suspended
                    # accounts in prune_users.py
                    pass
            self.logger.info("%s Finished pinging group %s", comment.id, group)
        self.logger.info("%s Finished pinging token %s", comment.id, token)

        # Edit reply to ping
        ping_comment_body = []
        for group in groups:
            with open("templates/ping_comment_group.txt") as f:
                ping_comment_group_template = string.Template(f.read())
            ping_comment_group = ping_comment_group_template.substitute(
                group=group,
                bot_username=self.username
            )
            ping_comment_body.append(ping_comment_group)
        root_comment = comment
        while root_comment.is_root is False:
            root_comment = root_comment.parent()
        if comment != root_comment:
            ping_comment_body.append(
                f"[Root comment link]({root_comment.permalink})"
            )
        with open("templates/ping_comment.txt") as f:
            ping_comment_template = string.Template(f.read())
        ping_comment = ping_comment_template.substitute(
            ping_comment_body="\n".join(ping_comment_body),
            bot_username=self.username,
            primary_subreddit=str(self.primary_subreddit)
        )
        reply.edit(ping_comment)
        self.logger.debug("%s Reply edited, done", comment.id)

    
    def message_error_reply(self, message, error):
        """Sends an error message

        Includes links to documentation and modmail
        """
        with open("templates/message_error_reply.txt") as f:
            body_template = string.Template(f.read())
        reply = body_template.substitute(
            error=error,
            primary_subreddit=str(self.primary_subreddit)
        )
        message.author.message(
            subject="Command Error",
            message = reply
        )


    def handle_message(self, message):
        """Handles messages"""

        self.logger.debug(
            "%s Handling message from %s", message.id, str(message.author)
        )
        words = message.body.lower().split()

        # Unsubscribe from all
        if words == ["unsubscribe"]:
            with self.db:
                with open("sql/functions/get_user_subscriptions.sql") as f:
                    arg = {"username": str(message.author).lower()}
                    unsubscribed_groups = [
                        g[0] for g in self.db.execute(f.read(), arg).fetchall()
                    ]
                with open("sql/functions/unsubscribe_user_from_all.sql") as f:
                    arg = {"username": str(message.author).lower()}
                    self.db.execute(f.read(), arg)
            resubscribe_groups = "subscribe " + "%26".join(unsubscribed_groups)
            with open("templates/unsubscribed_from_all.txt") as f:
                message_body_template = string.Template(f.read())
            message_body = message_body_template.substitute(
                bot_username=self.username,
                resubscribe_groups=resubscribe_groups
            )
            self.logger.info("%s unsubscribed from all groups", message.id)
            message.mark_read()
            message.author.message(
                subject="Unsubscribed from all groups",
                message=message_body
            )
            return

        # List my subscriptions
        if words[0] == "list_my_subscriptions":
            with self.db:
                with open("sql/functions/get_user_subscriptions.sql") as f:
                    arg = {"username": str(message.author).lower()}
                    groups = [
                        s[0] for s in self.db.execute(f.read(), arg).fetchall()
                    ]
            self.logger.info("%s Listing groups", message.id)
            message.mark_read()
            message.author.message(
                subject="Your Subscriptions",
                message="You are subscribed to groups: " + ", ".join(groups)
            )
            return

        # All remaining commands are in the form [command, group(s)]
        try:
            command = words[0]
            token = words[1].upper()
        except IndexError:
            self.logger.warning(
                "%s invalid command %s", message.id, message.body
            )
            message.mark_read()
            error = f"Invalid command"
            self.message_error_reply(message, error)
            return
        groups = token.split("&")
        commands = ("unsubscribe", "subscribe", "addtogroup")
        if command not in commands:
            self.logger.warning(
                "%s unrecognized command %s", message.id, command
            )
            message.mark_read()
            error = f"Unrecognized command {command}"
            self.message_error_reply(message, error)
            return

        # Validate groups within command
        for group in groups:
            if not pinglib.group_name_is_valid(group):
                self.logger.warning(
                    "%s group %s is invalid", message.id, group
                )
                message.mark_read()
                error = f"Group name {group} is invalid"
                self.message_error_reply(message, error)
                return

        # Ensure group(s) exist
        with self.db:
            with open("sql/functions/get_groups_and_aliases.sql") as f:
                db_groups = [
                    group[0] for group in self.db.execute(f.read()).fetchall()
                ]
        for group in groups:
            if group not in db_groups:
                self.logger.warning(
                    "%s group %s does not exist", message.id, group
                )
                message.mark_read()
                self.message_error_reply(message, f"{group} does not exist")
                return
        self.logger.debug("%s Group(s) exist", message.id)

        # De-alias our group list, ensure no duplicates
        with self.db:
            with open("sql/functions/de-alias.sql") as f:
                de_alias = {
                    item[0]: item[1]
                    for item
                    in self.db.execute(f.read()).fetchall()
                }
        groups = list(set([de_alias[group] for group in groups]))

        # Unsubscribe from group(s) but NOT all
        if command == "unsubscribe":
            for group in groups:
                with self.db:
                    with open("sql/functions/unsubscribe_user_from_group.sql") as f:
                        arg = {
                            "username": str(message.author).lower(),
                            "group_name": group
                        }
                        self.db.execute(f.read(), arg)
            self.logger.info("%s unsubcribed from %s", message.id, token)
            with open("templates/unsubscribed_from_group.txt") as f:
                message_body_template = string.Template(f.read())
            message_body = message_body_template.substitute(
                bot_username=self.username,
                token=token,
                url_token=token.replace("&", "%26")
            )
            message.mark_read()
            message.author.message(
                subject="Unsubscribed from group(s)",
                message=message_body
            )
            return

        # Subscribe to group (addtogroup kept for compatibility)
        if command == "subscribe" or command == "addtogroup":
            is_mod = str(message.author) in self.primary_subreddit.moderator()
            for group in groups:
                with self.db:
                    with open("sql/functions/is_protected.sql") as f:
                        protected = bool(self.db.execute(
                            f.read(), {"group_name": group}
                        ).fetchall()[0][0])
                if protected and not is_mod:
                    self.logger.warning(
                        "%s group %s is protected", message.id, group
                    )
                    error = (
                        f"Group {group} is protected. Contact the mods if you "
                        "want to subscribe to this group."
                    )
                    message.mark_read()
                    self.message_error_reply(message, error)
                    return
                with self.db:
                    with open("sql/functions/subscribe_user_to_group.sql") as f:
                        arg = {
                            "username": str(message.author).lower(),
                            "group_name": group,
                            "created_epoch_sec": message.created_utc
                        }
                        self.db.execute(f.read(), arg)
                self.logger.info(
                    "%s subscribed to %s", message.id, token
                )
            with open("templates/subscribed_to_group.txt") as f:
                message_body_template = string.Template(f.read())
            message_body = message_body_template.substitute(
                bot_username=self.username,
                token=token,
                url_token=token.replace("&", "%26")
            )
            message.mark_read()
            message.author.message(
                subject="Subscribed to group",
                message=message_body
            )


if __name__ == "__main__":
    """Main service function. Instantiate and run the bot continuously"""

    # Pass these as an argument so we can mock it for testing
    reddit = praw.Reddit(
        client_id=os.environ["CLIENT_ID"],
        client_secret=os.environ["CLIENT_SECRET"],
        refresh_token=os.environ["REFRESH_TOKEN"],
        user_agent="linux:user_pinger_2-bot:v0.0.1 (by /u/jenbanim)"
    )
    # TODO put in environment variables
    logger = slack_python_logging.getLogger(
        app_name = "user_pinger",
        slack_loglevel = "CRITICAL",
        stream_loglevel = "INFO"
    )
    user_pinger = UserPinger(reddit, logger)

    # Log uncaught exceptions to Slack before exiting
    def log_excepthook(ex_type, ex_value, ex_traceback):
        user_pinger.logger.critical(
            "Critical Exception caught, exiting",
            exc_info=(ex_type, ex_value, ex_traceback)
        )
    sys.excepthook = log_excepthook  # Wish I could use a lambda :pensive:

    # Main Loop
    recoverable_errors = (
        prawcore.exceptions.ServerError,
        prawcore.exceptions.ResponseException,
        prawcore.exceptions.RequestException,
        praw.exceptions.RedditAPIException
    )
    while True:
        try:
            user_pinger.listen()
        except recoverable_errors:
            user_pinger.logger.warning("Reddit API error - sleeping 1 minute")
            time.sleep(60)
