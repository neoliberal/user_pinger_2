-- Gets the ping log

-- Arguments: {after_epoch}

SELECT 
    ping_log.created_epoch_sec,
    ping_groups.name,
    ping_groups.category,
    ping_log.permalink 

FROM ping_log_group_ids 
    JOIN ping_log on ping_log_group_ids.comment_id = ping_log.comment_id 
    JOIN ping_groups ON ping_log_group_ids.group_id = ping_groups.group_id

WHERE ping_log.created_epoch_sec > :after_epoch;
