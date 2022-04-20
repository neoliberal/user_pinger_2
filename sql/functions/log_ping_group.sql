-- logs an individual group pinged in a comment

-- Arguments: {group_name, comment_id}

INSERT INTO ping_log_group_ids (
    group_id,
    comment_id
)
VALUES (
    (SELECT group_id FROM ping_groups WHERE name = :group_name),
    :comment_id
)
