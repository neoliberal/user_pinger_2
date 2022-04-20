-- Creates a group alias, API

-- Arguments: {group_alias, group_name}

INSERT OR IGNORE INTO group_aliases (
    group_alias,
    group_id
)
VALUES (
    :group_alias,
    (SELECT group_id 
        FROM (
            SELECT name, group_id 
            FROM ping_groups UNION SELECT group_alias AS name, group_id FROM group_aliases
        ) 
        WHERE name = :group_name
    )
)
