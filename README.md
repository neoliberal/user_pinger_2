# User Pinger 2

This is a Reddit bot, api, and website that allows users to "ping" groups on the subreddit [/r/neoliberal](https://reddit.com/r/neoliberal). Users may subscribe to a group such as KITTY, ping that group by writing a comment containing "!ping KITTY", and then everyone else who has subscribed to that group will receive a message with a link to that comment - which in this case would likely include a cat photo. Many groups exist for a variety of topics. Broadly, the purpose of this software is to allow users to more easily find content relevant to their interests that would otherwise be hidden among other submissions and comments

Further documentation on how to use the bot can be found on the [/r/neoliberal subreddit wiki documentation page](https://www.reddit.com/r/neoliberal/wiki/user_pinger_2). The website for managing subscriptions can be found [here](https://neoliber.al/user_pinger_2/)

This is a rewrite of [the original User Pinger](https://github.com/neoliberal/user_pinger) that implements many new QoL features, including:

* Multi-group pinging (eg. DOG&KITTY)
* Group aliases (eg. CAT refers to KITTY)
* Auto-generated documentation that includes an activity counter
* A website for users to manage subscriptions, and mods to manage groups
* A root comment button
* An undo button for when you accidentally unsubscribe from all

Planned features include:

* Making pings faster by removing inactive accounts
* A page for viewing statistics such as how many pings get sent per day

Possible features for the future include:

* Ping digests?
* Hide inactive groups?
