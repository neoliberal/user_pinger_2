from itertools import groupby
import os
import sqlite3
import string
import time

import praw

import slack_python_logging


def update(reddit, subreddit, after_epoch):
    """Update the wiki documentation"""

    # Get group documentation data
    primary_subreddit = subreddit.split("+")[0]
    db = sqlite3.connect(f"sql/db/{primary_subreddit}.db")
    cur = db.cursor()
    with open("sql/functions/init_db.sql") as f:
        db.executescript(f.read())
    with open("sql/functions/prepare_documentation.sql") as f:
        cur.execute(f.read(), {"after_epoch": after_epoch})
    with open("sql/functions/get_documentation.sql") as f:
        data = cur.execute(f.read()).fetchall()
    with open("sql/functions/count_groups.sql") as f:
        num_groups = cur.execute(f.read()).fetchall()[0][0]
    with open("sql/functions/count_subscriptions.sql") as f:
        num_subscriptions = cur.execute(f.read()).fetchall()[0][0]
    with open("sql/functions/count_users.sql") as f:
        num_users = cur.execute(f.read()).fetchall()[0][0]
    cur.close()
    db.close()

    # Format group documentation
    # Yes... ha ha ha... YES!
    categorized = [
        [
            sorted(subgroup[1], key = lambda x: x[0]) 
            for subgroup 
            in groupby(sorted(list(category[1]), key = lambda x: x[2].split(":")[-1][0]), lambda x: x[2].split(":")[-1][0])
        ] 
        for category
        in groupby(sorted(data, key = lambda x: x[2]), lambda x: x[2][0])
    ]

    # Create the ping documentation text
    lines = []
    lines.append(f"**Stats:** {num_groups} groups | {num_users} users | {num_subscriptions} subscriptions")
    for category in categorized:
        category_name = category[0][0][2].split(":")[0][2:]
        lines.extend([f"## {category_name}", ""])
        for subcategory in category:
            subcategory_name = subcategory[0][2].split(":")[-1][2:]
            if subcategory_name != category_name:
                lines.extend([f"### {subcategory_name}", ""])
            lines.append("Name | Description | Weekly Pings")
            lines.append("|---|---|---|")
            for group in subcategory:
                group_name = group[0]
                description = group[1]
                activity = f"[{group[5]}](https://neoliber.al/user_pinger_2/history.html?group_name={group[0]}&count=5)"
                protected = "protected" if group[3] else ""
                locked = "locked" if group[4] else ""
                attributes = ", ".join(filter(None, [locked, protected]))
                subscribe_url = (
                    "https://reddit.com/message/compose"
                    f"?to={reddit.user.me()}"
                    f"&subject=Subscribe%20to%20{group_name}"
                    f"&message=subscribe%20{group_name}"
                )
                name_and_attr = [f"[{group_name}]({subscribe_url})"]
                if attributes:
                    name_and_attr.extend([" (", attributes, ")"])
                name_and_attr = "".join(name_and_attr)
                lines.append(f"{name_and_attr} | {description} | {activity}")
            lines.append("")
    group_documentation = "\n".join(lines)

    # Build wiki documentation
    with open("templates/wiki.txt") as f:
        wiki_documentation_template = string.Template(f.read())
    wiki_documentation = wiki_documentation_template.substitute(
        subreddit = subreddit,
        primary_subreddit = primary_subreddit,
        bot_username = reddit.user.me(),
        group_documentation = group_documentation
    )

    # Edit wiki page
    reddit.subreddit(primary_subreddit).wiki["user_pinger_2"].edit(
        wiki_documentation,
        reason = "Automatic update"
    )


if __name__ == "__main__":
    """Main function called by service file"""

    reddit = praw.Reddit(
        client_id=os.environ["CLIENT_ID"],
        client_secret=os.environ["CLIENT_SECRET"],
        refresh_token=os.environ["REFRESH_TOKEN"],
        user_agent="linux:user_pinger_2-wiki_updater:v0.0.1 (by /u/jenbanim)"
    )
    # TODO put in environment variables
    logger = slack_python_logging.getLogger(
        app_name = "user_pinger-wiki_updater",
        slack_loglevel = "CRITICAL",
        stream_loglevel = "INFO"
    )
    after_epoch = time.time() - 60*60*24*7 # count pings in last week
    subreddit = os.environ["SUBREDDIT"]

    logger.info("Beginning update")
    update(reddit, subreddit, after_epoch)
    logger.info("Update complete")
