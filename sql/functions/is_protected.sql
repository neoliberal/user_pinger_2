-- Check if a group is protected (ie. only mods can subscribe)

-- Arguments: {group_name}

SELECT protected FROM ping_groups WHERE name = :group_name
