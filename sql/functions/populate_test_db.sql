-- This script populates our database with some example data. It is used by our
-- test cases as well as for development.

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
VALUES
    (
        0, 
        'ANNOUNCEMENTS',
        'Announcements pertaining to the subreddit and Neoliberal Project',
        '0 Special',
        0,
        1,
        0,
        1600000000
    ),
    (
        1,
        'USA-WA',
        'Washington State',
        '1 Places:1 US States, Cities & Regions',
        0,
        0,
        0,
        1600000000
    ),
    (
        2,
        'MODS',
        'Special mod-only ping',
        '0 Special',
        1,
        1,
        1,
        1600000000
    ),
    (
        3,
        'UKRAINE',
        'Слава Україні',
        '1 Places:0 Countries & Intl. Regions',
        0,
        0,
        0,
        1600000000
    ),
    -- single quotes are escaped by doubling them up
    (
        4,
        'CONTROVERSIAL',
        'A controversial group that anyone subscribed to the group can ping, but need mod permissions to subscribe',
        '3 Media & Entertainment:4 Online',
        1,
        0,
        0,
        1600000000
    ),
    (
        5,
        'BURPMAS',
        'No one knows, but it''s provocative',
        '4 People & Life:0 Interests & Fun',
        0,
        0,
        1,
        1600000000
    ),
    (
        6,
        'KITTY',
        'Cats',
        '4 People & Life:0 Interests & Fun',
        0,
        0,
        0,
        1600000000
    );

INSERT INTO group_aliases (
    group_alias,
    group_id
)
VALUES
    (
        'CAT',
        6
    );

-- remember USERNAMES MUST BE LOWERCASE
-- this ensures no duplicate subscriptions
INSERT INTO subscriptions (
    username,
    group_id,
    created_epoch_sec
)
VALUES
    (
        'jenbanim',
        0,
        '1600000000'
    ),
    (
        'jenbanim-2',
        6,
        1600000000
    ),
    (
        'foo',
        3,
        1600000000
    );

-- Using a real comment with a made up token
INSERT INTO ping_log (
    comment_id,
    permalink,
    author,
    token,
    created_epoch_sec
)
VALUES 
    (
        'hcmepdb',
        'https://www.reddit.com/r/neoliberal/comments/pmnxhh/discussion_thread/hcmepdb/',
        'jenbanim',
        'KITTY&USA-WA',
        '1631486662'
    ),
    (
        'i2e5jrb',
        'https://www.reddit.com/r/neoliberal/comments/tpeju5/discussion_thread/i2e5jrb/',
        'jenbanim',
        'USA-WA',
        '1648436328'
    );

INSERT INTO ping_log_group_ids (
    group_id,
    comment_id
)
VALUES 
    (
        6,
        'hcmepdb'
    ),
    (
        3,
        'hcmepdb'
    ),
    (
        3,
        'i2e5jrb'
    );
