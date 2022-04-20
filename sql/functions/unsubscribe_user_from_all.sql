-- Unsubscribes a user from ALL groups, API and bot

-- Arguments: {username}

DELETE FROM subscriptions
WHERE username = :username;
