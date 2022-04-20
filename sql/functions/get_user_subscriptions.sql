-- Gets a user's subscriptions, API and Bot

-- Arguments: {username}

SELECT name
FROM ping_groups
WHERE group_id in (
    SELECT group_id
    FROM subscriptions
    WHERE username = :username
);
