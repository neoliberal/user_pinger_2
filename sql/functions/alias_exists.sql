-- Check if an alias exists

-- Arguments: {alias_name}

SELECT CASE WHEN COUNT(group_alias) != 0 THEN 1 ELSE 0 END AS alias_exists FROM group_aliases WHERE group_alias = :alias_name