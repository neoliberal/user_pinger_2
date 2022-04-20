-- Unsubscribes user from group, API and bot

-- Arguments: {username, group_name}

-- Works with group aliases just in case someone writes the command message by
-- hand. All pre-formatted unsubscribe commands use the true name.

DELETE FROM subscriptions 
WHERE username = :username
AND group_id = (
    SELECT group_id FROM (
        SELECT name, group_id FROM
            ping_groups UNION SELECT group_alias AS name, group_id FROM group_aliases
    )
    WHERE name = :group_name
);
