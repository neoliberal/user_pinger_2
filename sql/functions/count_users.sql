-- Counts the number of unique subscribers
--
-- No arguments

SELECT count(*) FROM (SELECT * FROM subscriptions GROUP BY username);
