-- Get the aliases of a group using its official name

-- Arguments: {group_name}

SELECT group_alias FROM group_aliases WHERE group_id = (SELECT group_id FROM ping_groups WHERE name = :group_name)
