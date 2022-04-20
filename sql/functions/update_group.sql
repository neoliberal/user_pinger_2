-- Updates the details about a group

-- Arguments: {group_id, name, description, category, protected, locked, hidden}

UPDATE ping_groups SET
    name = :name, 
    description = :description, 
    category = :category,
    protected = :protected,
    locked = :locked,
    hidden = :hidden

WHERE group_id = :group_id
