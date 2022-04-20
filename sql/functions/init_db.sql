-- This file is executed by all scripts that interact with the database
-- This ensures there's always a db with the correct schema on a cold start
-- while the "IF NOT EXISTS" ensures we don't throw an error on a hot start

PRAGMA foreign_keys = ON;

-- group_id is separate from the name to allow for easy renaming
-- group_alias allows for eg. pinging CAT when the group is called KITTY
CREATE TABLE IF NOT EXISTS group_aliases (
    group_alias TEXT PRIMARY KEY,
    group_id INTEGER NOT NULL,
    FOREIGN KEY (group_id) REFERENCES ping_groups (group_id)
);

-- name is the authoritative one used in documentation and replies
-- categories are split into sub-categories by ":" eg. "0 foo:1 bar"
--     The leading integer is stripped and used for sorting
-- protected means only mods can subscribe
-- locked means only mods can ping
-- hidden means it won't be displayed on doc pages
CREATE TABLE IF NOT EXISTS ping_groups (
    group_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    category TEXT NOT NULL,
    protected INTEGER NOT NULL,
    locked INTEGER NOT NULL,
    hidden INTEGER NOT NULL,
    created_epoch_sec INTEGER NOT NULL
);

-- usernames MUST be all lowercase
CREATE TABLE IF NOT EXISTS subscriptions (
    username TEXT NOT NULL,
    group_id INTEGER NOT NULL,
    created_epoch_sec INTEGER NOT NULL,
    PRIMARY KEY (username, group_id),
    FOREIGN KEY (group_id) REFERENCES ping_groups (group_id)
);

-- The permalink contains both the submission ID and the comment ID so it's
-- somewhat redundant. However, this cuts down on the parsing required for our
-- log viewer
CREATE TABLE IF NOT EXISTS ping_log (
    comment_id TEXT PRIMARY KEY,
    permalink TEXT NOT NULL,
    author TEXT NOT NULL,
    token TEXT NOT NULL,
    created_epoch_sec INTEGER NOT NULL
);

-- Because individual comments can ping multiple groups, we use this table to
-- "expand" the token into the individual groups. So you can get all pings for
-- KITTY for example by selecting the appropriate group ID from this table and
-- joining it with the ping_log table
CREATE TABLE IF NOT EXISTS ping_log_group_ids (
    group_id INTEGER NOT NULL,
    comment_id TEXT NOT NULL,
    PRIMARY KEY (group_id, comment_id),
    FOREIGN KEY (group_id) REFERENCES ping_groups (group_id),
    FOREIGN KEY (comment_id) REFERENCES ping_log (comment_id)
);
