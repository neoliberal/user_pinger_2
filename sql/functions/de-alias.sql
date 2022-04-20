-- Returns a two column table with names and aliases on the left, and only true names on the right

-- No arguments

SELECT temp.name, ping_groups.name FROM (SELECT name, group_id FROM ping_groups UNION SELECT group_alias AS name, group_id FROM group_aliases) AS temp JOIN ping_groups on temp.group_id = ping_groups.group_id;
