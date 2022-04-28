-- Prepares a table for use in the get_documentation.sql script

-- Arguments: {after_epoch}

CREATE TEMPORARY TABLE ping_count AS
SELECT group_id, COUNT(*) AS count
FROM ping_log_group_ids
    JOIN ping_log ON ping_log_group_ids.comment_id = ping_log.comment_id
WHERE ping_log.created_epoch_sec > :after_epoch
GROUP BY group_id;
