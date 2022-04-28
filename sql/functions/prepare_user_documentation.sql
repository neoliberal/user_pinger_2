-- Prepares a table for use in the get_documentation.sql script
-- You must call prepare_documentation.sql first

-- Arguments: {username}

CREATE TEMPORARY TABLE user_subscriptions AS
SELECT *
FROM subscriptions
WHERE username = :username
