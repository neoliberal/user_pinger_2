-- Log a pinged comment

-- Arguments: {
--     comment_id,
--     permalink,
--     author,
--     token,
--     created_epoch_sec
-- }

INSERT INTO ping_log (
    comment_id,
    permalink,
    author,
    token,
    created_epoch_sec
)
VALUES (
    :comment_id,
    :permalink,
    :author,
    :token,
    :created_epoch_sec
)
