# TODO refactor such that importing this runs the API socket
# Then set up the unit tests so they make calls to the API using
# requests-unixsocket on pypi

# TODO logging

from itertools import groupby
import os
import re
import requests
import sqlite3
import time
from typing import List, Union

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
import praw
from pydantic import BaseModel
from typing_extensions import TypedDict
import uvicorn

import pinglib


api = FastAPI()

@api.get(path="/api/me")
def get_user(access_token: str) -> str:
    """
    Returns the name of the Reddit user corresponding to the access token.
    There's probably a better way to do this in praw, but it eludes me
    """
    try:
        assert re.match("^[a-zA-Z0-9-_.]+$", access_token)
    except AssertionError:
        # Malformed access token
        raise HTTPException(status_code=401, detail="Malformed access token")
    reddit_user_agent = "linux:user_pinger_v2-api:v0.0.1 (by /u/jenbanim)"
    auth = requests.get(
        "https://oauth.reddit.com/api/v1/me",
        headers={
            "User-Agent": reddit_user_agent,
            "Authorization": f"bearer {access_token}"
        }
    )
    if auth.status_code == 401:
        # Invalid access token
        raise HTTPException(status_code=401, detail="Invalid access token")
    elif auth.status_code !=200:
        # Some other problem
        raise HTTPException(status_code=500, detail="Unknown error reaching Reddit")
    return auth.json()["name"]


def group_is_valid_and_exists(group: str) -> bool:
    if not pinglib.group_name_is_valid(group):
        return False
    subreddit = os.environ["SUBREDDIT"].split("+")[0]
    db = sqlite3.connect(f"sql/db/{subreddit}.db")
    with db:
        with open("sql/functions/init_db.sql") as f:
            db.executescript(f.read())
        with open("sql/functions/get_groups_and_aliases.sql") as f:
            db_groups = [
                group[0] for group in db.execute(f.read()).fetchall()
            ]
    if group not in db_groups:
        return False
    return True


def alias_exists(alias: str) -> bool:
    subreddit = os.environ["SUBREDDIT"].split("+")[0]
    db = sqlite3.connect(f"sql/db/{subreddit}.db")
    with db:
        with open("sql/functions/init_db.sql") as f:
            db.executescript(f.read())
        with open("sql/functions/alias_exists.sql") as f:
            exists = bool(db.execute(f.read(), {"alias_name": alias}).fetchall()[0][0])
    if exists:
        return True
    return False


def is_mod(username):
    reddit = praw.Reddit(
        client_id=os.environ["CLIENT_ID"],
        client_secret=os.environ["CLIENT_SECRET"],
        refresh_token=os.environ["REFRESH_TOKEN"],
        user_agent="linux:user_pinger_2-api:v0.0.1 (by /u/jenbanim)"
    )
    subreddit = os.environ["SUBREDDIT"].split("+")[0]
    return username in reddit.subreddit(subreddit).moderator()


@api.post(path="/api/subscribe")
def subscribe(access_token: str, group: str) -> str:
    username = get_user(access_token)
    subreddit = os.environ["SUBREDDIT"].split("+")[0]
    if not group_is_valid_and_exists(group):
        raise HTTPException(status_code=400, detail="Invalid group")
    db = sqlite3.connect(f"sql/db/{subreddit}.db")
    with db:
        with open("sql/functions/init_db.sql") as f:
            db.executescript(f.read())
        with open("sql/functions/is_protected.sql") as f:
            protected = bool(db.execute(
                f.read(), {"group_name": group}
            ).fetchall()[0][0])
    if protected:
        if not is_mod(username):
            raise HTTPException(status_code=403, detail="Group protected")
    with db:
        with open("sql/functions/subscribe_user_to_group.sql") as f:
            arg = {
                "username": username.lower(),
                "group_name": group,
                "created_epoch_sec": int(time.time())
            }
            db.execute(f.read(), arg)
    return "success"


@api.post(path="/api/unsubscribe")
def unsubscribe(access_token: str, group: str) -> str:
    username = get_user(access_token)
    subreddit = os.environ["SUBREDDIT"].split("+")[0]
    if not group_is_valid_and_exists(group):
        raise HTTPException(status_code=400, detail="Invalid group")
    db = sqlite3.connect(f"sql/db/{subreddit}.db")
    with db:
        with open("sql/functions/init_db.sql") as f:
            db.executescript(f.read())
        with open("sql/functions/unsubscribe_user_from_group.sql") as f:
            arg = {
                "username": username.lower(),
                "group_name": group,
            }
            db.execute(f.read(), arg)
    return "success"


@api.post(path="/api/subscribe_user")
def subscribe_user(access_token: str, user: str, group:str) -> str:
    username = get_user(access_token)
    subreddit = os.environ["SUBREDDIT"].split("+")[0]
    if not is_mod(username):
        raise HTTPException(status_code=403, detail="You must be a mod")
    if not re.match("^[a-zA-Z0-9_-]{1,20}$", user):
        raise HTTPException(status_code=400, detail="Invalid user")
    if not group_is_valid_and_exists(group):
        raise HTTPException(status_code=400, detail="Invalid group")
    db = sqlite3.connect(f"sql/db/{subreddit}.db")
    with db:
        with open("sql/functions/init_db.sql") as f:
            db.executescript(f.read())
        with open("sql/functions/subscribe_user_to_group.sql") as f:
            arg = {
                "username": user.lower(),
                "group_name": group,
                "created_epoch_sec": int(time.time())
            }
            db.execute(f.read(), arg)
    return "success"


@api.post(path="/api/unsubscribe_user")
def unsubscribe_user(access_token: str, user: str, group:str) -> str:
    username = get_user(access_token)
    subreddit = os.environ["SUBREDDIT"].split("+")[0]
    if not is_mod(username):
        raise HTTPException(status_code=403, detail="You must be a mod")
    if not re.match("^[a-zA-Z0-9_-]{1,20}$", user):
        raise HTTPException(status_code=400, detail="Invalid user")
    if not group_is_valid_and_exists(group):
        raise HTTPException(status_code=400, detail="Invalid group")
    db = sqlite3.connect(f"sql/db/{subreddit}.db")
    with db:
        with open("sql/functions/init_db.sql") as f:
            db.executescript(f.read())
        with open("sql/functions/unsubscribe_user_from_group.sql") as f:
            arg = {
                "username": user.lower(),
                "group_name": group,
            }
            db.execute(f.read(), arg)
    return "success"


@api.post(path="/api/create_alias")
def create_alias(access_token: str, alias: str, group: str) -> str:
    username = get_user(access_token)
    subreddit = os.environ["SUBREDDIT"].split("+")[0]
    if not is_mod(username):
        raise HTTPException(status_code=403, detail="You must be a mod to create an alias")
    alias = alias.upper()
    group = de_alias_group(group)
    if not pinglib.group_name_is_valid(alias):
        raise HTTPException(status_code=400, detail="Invalid alias")
    if not group_is_valid_and_exists(group):
        raise HTTPException(status_code=400, detail="Invalid group")
    if group_is_valid_and_exists(alias):
        raise HTTPException(status_code=409, detail="Alias already in use as group name")
    if alias_exists(alias):
        raise HTTPException(status_code=409, detail="Alias already in use for another group")
    db = sqlite3.connect(f"sql/db/{subreddit}.db")
    with db:
        with open("sql/functions/init_db.sql") as f:
            db.executescript(f.read())
        with open("sql/functions/create_alias.sql") as f:
            arg = {
                "group_alias": alias,
                "group_name": group
            }
            db.execute(f.read(), arg)
    return "success"


@api.post(path="/api/delete_alias")
def delete_alias(access_token: str, alias: str) -> str:
    username = get_user(access_token)
    alias = alias.upper()
    if not pinglib.group_name_is_valid(alias):
        raise HTTPException(status_code=400, detail="Invalid alias")
    subreddit = os.environ["SUBREDDIT"].split("+")[0]
    if not is_mod(username):
        raise HTTPException(status_code=403, detail="You must be a mod to create an alias")
    db = sqlite3.connect(f"sql/db/{subreddit}.db")
    with db:
        with open("sql/functions/init_db.sql") as f:
            db.executescript(f.read())
        with open("sql/functions/delete_alias.sql") as f:
            arg = {
                "group_alias": alias,
            }
            db.execute(f.read(), arg)
    return "success"


@api.get(path="/api/de_alias_group")
def de_alias_group(alias: str) -> str:
    alias = alias.upper()
    subreddit = os.environ["SUBREDDIT"].split("+")[0]
    if not group_is_valid_and_exists(alias):
        raise HTTPException(status_code=400, detail="Invalid group")
    db = sqlite3.connect(f"sql/db/{subreddit}.db")
    cur = db.cursor()
    with db:
        with open("sql/functions/init_db.sql") as f:
            db.executescript(f.read())
        with open("sql/functions/de-alias.sql") as f:
            de_alias = {
                item[0]: item[1]
                for item
                in db.execute(f.read()).fetchall()
            }
            group = de_alias[alias]
    db.close()
    return group


@api.get(path="/api/get_group_aliases")
def get_group_aliases(alias: str) -> List[str]:
    group = de_alias_group(alias)
    subreddit = os.environ["SUBREDDIT"].split("+")[0]
    db = sqlite3.connect(f"sql/db/{subreddit}.db")
    cur = db.cursor()
    with db:
        with open("sql/functions/init_db.sql") as f:
            db.executescript(f.read())
        with open("sql/functions/get_group_aliases.sql") as f:
            arg = {"group_name": group}
            aliases = [item[0] for item in cur.execute(f.read(), arg).fetchall()]
    db.close()
    return aliases


@api.get(path="/api/get_ping_log")
def get_ping_log(
    epoch_sec: int,
    group_name: str,
    sort: str,
    count: int
) -> List:
    try:
        assert sort in ("ASC", "DESC")
    except AssertionError:
        raise HTTPException(status_code=400, detail="Sort must be ASC or DESC")
    try:
        assert 1 <= count <= 50
    except AssertionError:
        raise HTTPException(
            status_code=400, detail="count must be between 1 and 50"
        )
    if not group_is_valid_and_exists(group_name):
        raise HTTPException(
            status_code=400, detail="Group is invalid or does not exist"
        )
    subreddit = os.environ["SUBREDDIT"].split("+")[0]
    db = sqlite3.connect(f"sql/db/{subreddit}.db")
    cur = db.cursor()
    with db:
        with open("sql/functions/init_db.sql") as f:
            db.executescript(f.read())
        arg = {
            "epoch_sec": epoch_sec, "group_name": group_name, "count": count
        }
        if sort == "ASC":
            with open("sql/functions/get_ping_log_after.sql") as f:
                ping_log = cur.execute(f.read(), arg).fetchall()
        else:
            # Can assume sort is DESC
            with open("sql/functions/get_ping_log_before.sql") as f:
                ping_log = cur.execute(f.read(), arg).fetchall()
    db.close()
    return ping_log


@api.get(path="/api/get_new_groups")
def get_new_groups(after_epoch: int) -> List[List[str]]:
    subreddit = os.environ["SUBREDDIT"].split("+")[0]
    db = sqlite3.connect(f"sql/db/{subreddit}.db")
    cur = db.cursor()
    with db:
        with open("sql/functions/init_db.sql") as f:
            db.executescript(f.read())
        with open("sql/functions/get_new_groups.sql") as f:
            arg = {"after_epoch": after_epoch}
            new_groups = cur.execute(f.read(), arg).fetchall()
    db.close()
    return new_groups


@api.get(path="/api/get_group_subscribers")
def get_group_subscribers(access_token:str, group):
    group = group.upper()
    subreddit = os.environ["SUBREDDIT"].split("+")[0]
    username = get_user(access_token)
    if not is_mod(username):
        raise HTTPException(status_code=403, detail="You must be a mod to get group subscribers")
    if not pinglib.group_name_is_valid(group):
        raise HTTPException(status_code=400, detail="Invalid group")
    if not group_is_valid_and_exists(group):
        raise HTTPException(status_code=404, detail="Group not found")
    db = sqlite3.connect(f"sql/db/{subreddit}.db")
    cur = db.cursor()
    with db:
        with open("sql/functions/init_db.sql") as f:
            db.executescript(f.read())
        with open("sql/functions/de-alias.sql") as f:
            de_alias = {
                item[0]: item[1]
                for item
                in db.execute(f.read()).fetchall()
            }
            group = de_alias[group]
        with open("sql/functions/get_group_subscribers.sql") as f:
            arg = {"group_name": group}
            subscribers = cur.execute(f.read(), arg).fetchall()
    db.close()
    return subscribers


class SubCategory(TypedDict):
    subcategory_name: Union[str, None]
    groups: List


class Category(TypedDict):
    category_name: str
    subcategories: List[SubCategory]


class UpdateGroups(TypedDict):
    access_token: str
    groups: List[Category]


@api.get(path="/api/list_user_groups")
def list_user_groups(access_token:str, target_user:str) -> List[Category]:
    """List a user's groups on the website"""
    username = get_user(access_token)
    if not is_mod(username):
        raise HTTPException(status_code=403, detail="You must be a mod to view a user's subsriptions")
    if not re.match("^[a-zA-Z0-9_-]{1,20}$", target_user):
        raise HTTPException(status_code=400, detail="Invalid target user")
    return get_groups(username, target_user.lower())


@api.get(path="/api/list_groups")
def list_groups(access_token:str) -> List[Category]:
    """List the groups for display on the website"""
    username = get_user(access_token).lower()
    return get_groups(username, username)


def get_groups(username: str, target_user:str) -> List[Category]:
    """Get a users groups"""
    after_epoch = time.time() - 60*60*24*7
    subreddit = os.environ["SUBREDDIT"].split("+")[0]
    db = sqlite3.connect(f"sql/db/{subreddit}.db")
    cur = db.cursor()
    with open("sql/functions/init_db.sql") as f:
        db.executescript(f.read())
    with open("sql/functions/prepare_documentation.sql") as f:
        cur.execute(f.read(), {"after_epoch": after_epoch})
    with open("sql/functions/prepare_user_documentation.sql") as f:
        cur.execute(f.read(), {"username": target_user})
    if is_mod(username):
        with open("sql/functions/get_mod_documentation.sql") as f:
            data = cur.execute(f.read()).fetchall()
    else:
        with open("sql/functions/get_user_documentation.sql") as f:
            data = cur.execute(f.read()).fetchall()
    db.close()
    # I apologize for this absolutely sweet list comprehension
    # TODO pit in pinglib? I use this twice
    categorized = [
        [
            sorted(subgroup[1], key = lambda x: x[0])
            for subgroup
            in groupby(
                sorted(list(category[1]), key = lambda x: x[2].split(":")[-1][0]),
                lambda x: x[2].split(":")[-1][0]
            )
        ]
        for category
        in groupby(sorted(data, key = lambda x: x[2]), lambda x: x[2][0])
    ]
    doc = []
    for cat_idx, category in enumerate(categorized):
        category_name = category[0][0][2].split(":")[0][2:]
        doc.append({
            "category_name": category_name,
            "subcategories": []
        })
        for subcat_idx, subcategory in enumerate(category):
            subcategory_name = subcategory[0][2].split(":")[-1][2:]
            if subcategory_name == category_name:
                subcategory_name = None
            doc[cat_idx]["subcategories"].append({
                "subcategory_name": subcategory_name,
                "groups": []
            })
            for group in subcategory:
                formatted_group = [
                    group[5], # subscribed
                    group[0], # name
                    group[1], # description
                    group[3], # protected
                    group[4], # activity
                    group[6], # hidden
                    group[7], # locked
                    group[8], # group_id
                ]
                doc[cat_idx]["subcategories"][subcat_idx]["groups"].append(
                    formatted_group
                )
    return doc


@api.post(path="/api/update_groups")
def update_groups(config: UpdateGroups):
    """Update the ping_groups database"""

    username = get_user(config["access_token"])
    if not is_mod(username):
        raise HTTPException(status_code=403, detail="You must be a mod")

    # TODO make sure that simultaneous edits don't screw things up
    # TODO validate
    # TODO call update_wiki
    # Build new group table
    groups = []
    for cat_idx, category in enumerate(config["groups"]):
        category_name = f"{cat_idx} {category['category_name']}"
        if ":" in category_name:
            raise HTTPException(status_code=400, detail="Invalid category")
        for subcat_idx, subcategory in enumerate(category["subcategories"]):
            subcategory_name = subcategory["subcategory_name"]
            if subcategory_name is not None:
                if ":" in subcategory_name:
                    raise HTTPException(
                        status_code=400, detail="Invalid subcategory"
                    )
            if subcategory_name is not None:
                subcategory_name = f"{subcat_idx} {subcategory_name}"
            for group in subcategory["groups"]:
                group_id = group[7]
                name = group[1]
                if not pinglib.group_name_is_valid(name):
                    raise HTTPException(
                        status_code=400, detail="Invalid group name"
                    )
                if alias_exists(name):
                    raise HTTPException(
                        status_code=409, detail="Group name conflicts with existing alias"
                    )
                description = group[2]
                category = ":".join(filter(None, [category_name, subcategory_name]))
                protected = group[3]
                locked = group[6]
                hidden = group[5]
                groups.append([
                    group_id,
                    name,
                    description,
                    category,
                    protected,
                    locked,
                    hidden
                ])
    groups.sort(key = lambda x: x[0])

    # Insert/update groups
    subreddit = os.environ["SUBREDDIT"].split("+")[0]
    db = sqlite3.connect(f"sql/db/{subreddit}.db")
    with db:
        with open("sql/functions/init_db.sql") as f:
            db.executescript(f.read())
        existing_group_ids = [
            g[0] for g in db.execute("SELECT group_id FROM ping_groups;").fetchall()
        ]
        for group in groups:
            arg = {
                "group_id": group[0],
                "name": group[1],
                "description": group[2],
                "category": group[3],
                "protected": group[4],
                "locked": group[5],
                "hidden": group[6],
                "created_epoch_sec": int(time.time())
            }
            if group[0] in existing_group_ids:
                with open("sql/functions/update_group.sql") as f:
                    db.execute(f.read(), arg)
            else:
                with open("sql/functions/create_group.sql") as f:
                    db.execute(f.read(), arg)
    return "success"

api_path = os.path.abspath(__file__)
pinger_dir = os.path.dirname(api_path)
static_files_dir = os.path.join(pinger_dir, 'www')
api.mount("/", StaticFiles(directory=static_files_dir), name="static")

if __name__ == "__main__":
    uvicorn.run(api, port=5000)
