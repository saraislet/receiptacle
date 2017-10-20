# Receiptacle

See [Product Requirements Document](https://docs.google.com/document/d/1DEG3YQdK9DUapkh737I_Px3GQLEZ3EnjVVPX0hj2dA0/edit?usp=sharing) on Google Docs.

I want to make accountable blocklists easy by allowing users to look up evidence for why a user is on a targeted blocklist like @NaziBlocker (e.g., pointing out swastikas in a profile image, 14 words in their profile description, or tweets/retweets of explicit white supremacist ideology).

One simple application of this receipts database would be allowing users to DM a bot, include an @$bot_screen_name in a reply, or quote-tweet to have the bot block the indicated user and store the indicated tweet as a receipt for why that user was blocked. Any blocklist could take advantage of such a tool.

## Prototype
Testing live prototype of back-end at https://young-meadow-72614.herokuapp.com/receipts
Raw JSON: https://young-meadow-72614.herokuapp.com/receipts_json

## TODO:
* Test front-end
* Plan additional features for CRUD MVP