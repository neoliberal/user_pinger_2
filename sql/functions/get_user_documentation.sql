-- Generates the documentation page used by api.py
-- This is the non-mod version that doesn't include hidden groups

-- You MUST call prepare_documentation.sql AND prepare_user_documentation.sql 
-- before this to avoid getting stale data.

-- Arguments: {after_epoch}

-- For some unholy reason SQLite throws a syntax error if I put parentheses
-- arount this SELECT clause

SELECT
    ping_groups.name,
    ping_groups.description,
    ping_groups.category,
    ping_groups.protected,
    CASE WHEN ping_count.count IS NULL THEN 0 ELSE ping_count.count END AS num_pings,
    CASE WHEN user_subscriptions.username IS NULL THEN 0 ELSE 1 END AS subscribed,
    ping_groups.hidden,
    ping_groups.locked,
    ping_groups.group_id

FROM ping_groups 
LEFT JOIN ping_count ON ping_groups.group_id = ping_count.group_id
LEFT JOIN user_subscriptions on ping_groups.group_id = user_subscriptions.group_id
WHERE ping_groups.created_epoch_sec > :after_epoch
AND ping_groups.hidden < 1;
