-- Gets the ping log starting at a particular epoch_sec and continuing backwards

-- Arguments: {epoch_sec, group_name, count}

SELECT 
    ping_log.created_epoch_sec,
    ping_groups.name,
    ping_log.permalink 

FROM ping_log_group_ids 
    JOIN ping_log on ping_log_group_ids.comment_id = ping_log.comment_id 
    JOIN ping_groups ON ping_log_group_ids.group_id = ping_groups.group_id

WHERE 
    ping_log.created_epoch_sec < :epoch_sec
    AND ping_log_group_ids.group_id = ( 
    SELECT group_id 
        FROM (
            SELECT name, group_id FROM ping_groups UNION SELECT group_alias AS name, group_id FROM group_aliases
        )   
        WHERE name = :group_name
)

ORDER BY ping_log.created_epoch_sec DESC

LIMIT :count;
