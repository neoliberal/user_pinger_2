SELECT name FROM (
    SELECT name FROM ping_groups UNION SELECT group_alias AS name FROM group_aliases
);
