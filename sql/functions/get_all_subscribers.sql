-- Get a list of all people who are subscribed a group, no duplicates

-- Arguments: None

SELECT username FROM subscriptions GROUP BY username;
