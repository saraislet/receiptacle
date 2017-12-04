# Receiptacle

See [Product Requirements Document](https://docs.google.com/document/d/1DEG3YQdK9DUapkh737I_Px3GQLEZ3EnjVVPX0hj2dA0/edit?usp=sharing) on Google Docs.

I want to make accountable blocklists easy by allowing users to look up evidence for why a user is on a targeted blocklist like @NaziBlockbot (e.g., pointing out swastikas in a profile image, 14 words in their profile description, or racist/white supremacist harassment).

One simple application of this receipts database would be allowing users to DM a bot to have the bot block the indicated user and store the indicated tweet as a receipt for why that user was blocked. Any blocklist could take advantage of such a tool.

## Prototype
Testing live prototype of back-end at https://young-meadow-72614.herokuapp.com

## File structure

    .
    ├── crud.py                  # CRUD methods
    ├── main.py                  # Flask routes
    ├── parsing.py               # mostly regex for parsing inputs and tweets
    ├── Procfile                 # defines run command for Heroku
    ├── requirements.txt         # defines requirements for Heroku
    ├── runtime.txt              # defines Python version for Heroku
    ├── sign_in.py               # Twitter OAuth methods
    ├── Sturmtest.py             # old test version of Nazi classification engine
    ├── test_parsing.py          # unit tests
    ├── utils.py                 # basic utility methods (db_connect() and get_api())
    │
    ├── static
    │   └── css
    │       └── main.css
    │
    └── templates
        ├── app.html             # Nazi classification UI from Sturmjäger
        ├── approvals.html       # For approving receipts (logged in blocklist admins only)
        ├── error.html           # Generic error page
        ├── layout.html          # Template (includes header & footer)
        ├── results_table.html   # displays receipts or search results
        └── start.html           # login page

## TODO:
* Plan additional features for CRUD MVP
* Build unit tests.
  * Mock post and get requests.
* Build demo mode.
* Join SQL queries on accounts table to pull account data.
* Create route to single receipt by ID
* Create route to all receipts by the logged-in user (if not logged-in, redirect to login page)
* Configure and test digitalocean droplet

### NaziBlockBot todo:
* Insert into new status_id column.
* Write a script to update status_id in existing data.
* Respond to tweets with a link to the created receipt.
* Handle errors gracefully.