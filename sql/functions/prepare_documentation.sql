-- Prepares a table for use in the get_documentation.sql script

-- Arguments: None

DROP TABLE IF EXISTS ping_count;
DROP TABLE IF EXISTS user_subscriptions;

CREATE TEMPORARY TABLE ping_count AS
SELECT group_id, COUNT(*) AS count
FROM ping_log_group_ids
GROUP BY group_id;
