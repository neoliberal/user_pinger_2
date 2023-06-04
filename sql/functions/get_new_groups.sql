-- Gets newly created groups for the DT body text

-- Arguments: {after_epoch}

SELECT 
    name,
    description
FROM ping_groups
WHERE
    NOT hidden
    AND created_epoch_sec > :after_epoch;
