-- Gets a list of subscribers to a group, used for pings within bot. 
-- Also exposed on API, where it is mod only

-- Arguments: {group_name}

-- It might make more sense for this to be called with the group_id rather than
-- the (possibly aliased) group name

SELECT username 
FROM subscriptions 
WHERE group_id = (
    SELECT group_id 
        FROM (
            SELECT name, group_id FROM ping_groups UNION SELECT group_alias AS name, group_id FROM group_aliases
        )
        WHERE name = :group_name
)
