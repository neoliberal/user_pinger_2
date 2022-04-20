-- Create a new group, API only

-- Arguments: {
--     group_id, 
--     name,
--     description,
--     category,
--     protected,
--     locked,
--     hidden,
--     created_epoch_sec
-- }

INSERT INTO ping_groups (
    group_id,
    name,
    description,
    category,
    protected,
    locked,
    hidden,
    created_epoch_sec
)
VALUES (
    :group_id,
    :name,
    :description,
    :category,
    :protected,
    :locked,
    :hidden,
    :created_epoch_sec
)
