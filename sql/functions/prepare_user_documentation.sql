-- Prepares a table for use in the get_documentation.sql script

-- Arguments: username

CREATE TEMPORARY TABLE user_subscriptions AS
SELECT *
FROM subscriptions
WHERE username = :username
