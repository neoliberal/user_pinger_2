-- Check if a group is locked (ie. only mods can ping)

-- Arguments: {group_name}

SELECT locked FROM ping_groups WHERE name = :group_name
