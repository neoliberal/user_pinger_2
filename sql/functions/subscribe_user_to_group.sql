-- Subscribes user to group, API and bot

-- Arguments: {username, group_name, created_epoch_sec}

-- Works with group aliases just in case someone writes the command message by
-- hand. All pre-formatted subscribe commands use the true name.

INSERT OR IGNORE INTO subscriptions (
    username,
    group_id,
    created_epoch_sec
)
VALUES (
    :username,
    (SELECT group_id 
        FROM (
            SELECT name, group_id 
            FROM ping_groups UNION SELECT group_alias AS name, group_id FROM group_aliases
        ) 
        WHERE name = :group_name
    ),
    :created_epoch_sec
)
