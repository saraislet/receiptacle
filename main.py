# -*- coding: utf-8 -*-
"""
Created on Tue Sep 12 20:12:44 2017

@author: Sarai
"""

import os, json
from flask import Flask, request, render_template, redirect, session
import tweepy
import pymysql.cursors
import parsing, crud
#import Sturmtest as st

app = Flask(__name__)
app.secret_key = os.environ['session_secret_key']

consumer_key = os.environ['consumer_key']
consumer_secret = os.environ['consumer_secret']

#hostname = 'localhost:5000'
hostname = 'https://young-meadow-72614.herokuapp.com'
callback_url = hostname + '/verify'


def db_connect():
    # Connect to the database
    # The connection will be sent to crud.py methods as needed.
    try:
        connection = pymysql.connect(host = os.environ['host'],
                                     user = os.environ['user'],
                                     password = os.environ['password'],
                                     db = os.environ['database'],
                                     charset = 'utf8mb4',
                                     cursorclass = pymysql.cursors.DictCursor)
        return connection
    except BaseException as e:
        print("Error in db_connect():", e)
        raise OSError("Cannot connect to database.")
        return


def get_api():
    # Rebuild OAuthHandler and return tweepy.API(auth) if session exists.
    # Otherwise, return error_msg.
    
    try:
        # Build OAuthHandler
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(session['key'], session['secret'])
        return tweepy.API(auth)
    except tweepy.TweepError:
        print('Error! Failed to build OAuthHandler!')
        raise OSError("Cannot connect to Twitter API.")
        return


#@app.route('/')
#def temporary_redirect():
#    # Until the rest of the app is built, redirect to receipts.
#    return redirect("/receipts", code=302)


@app.route('/')
def send_token():
    redirect_url = ""
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret, callback_url)

    try: 
        #get the request tokens
        redirect_url= auth.get_authorization_url()
        session['request_token'] = auth.request_token
        
        return render_template('start.html', redirect_url = redirect_url)
    except tweepy.TweepError:
        error_msg = 'Error! Failed to get request token'
        print(error_msg)
        
        # TODO: Ideally, this would return an error message. Test this.
        return render_template('error.html', error_msg = error_msg)


@app.route("/verify")
def get_verification():
    # Get the verifier key from the request url.
    verifier = request.args['oauth_verifier']

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    print("session dict object is: " + str(session))
    token = session['request_token']
    del session['request_token']

    auth.request_token = token

    try:
        auth.get_access_token(verifier)
        api = tweepy.API(auth)
        
        # Store key and secret in session.
        # get_api() rebuilds OAuthHandler and returns tweepy.API(auth)
        session['key'] = auth.access_token
        session['secret'] = auth.access_token_secret
        session['logged_in'] = True
        session['user_id'] = api.me().id
        session['blocklist_ids'] = crud.check_admins(session['user_id'], db_connect())
        
        if session['blocklist_ids'] is not []:
            session['show_approvals'] = True

        
        return redirect("/receipts", code=302)
        
    except tweepy.TweepError:
        error_msg = 'Error! Failed to get access token.'
        print(error_msg)
        
        return render_template('error.html', error_msg = error_msg)
    
    except BaseException as e:
        print("Error in receipts():", e)
        return render_template('error.html', error_msg = error_msg)


@app.route("/approve")
def approvals(approval_msg=""):
    
    connection = db_connect()
    receipts = []
    show_error = False
        
    try:    
        with connection.cursor() as cursor:
            # Fetch the most recent 20 records that are approved
            sql = "SELECT * FROM `receipts`"
            sql += " WHERE `approved_by_id` IS NULL"
            sql += " ORDER BY `id` DESC LIMIT 20"
            cursor.execute(sql,)
            receipts = cursor.fetchall()
            
            # If a matching record exists, return result, otherwise return message.
            if len(receipts) == 0:
                print("Results array is empty. Something went wrong.")
            else:
                print("Returning receipts in array.")
                
    except BaseException as e:
        show_error = True
        error_msg = e
        print("Error in approve():", e)    
    
    # Don't show list of results if there aren't any.
    if len(receipts) > 0:
        show_results = True
    else:
        show_results = False
        
    if approval_msg is not "":
        show_approval_msg = True
    
    return render_template('approvals.html', 
                             results = receipts,
                             num_receipts = len(receipts),
                             logged_in = session['logged_in'],
                             show_approvals = session['show_approvals'],
                             show_approval_msg = show_approval_msg,
                             show_results = show_results,
                             show_error = show_error,
                             error_msg = error_msg,
                             approval_msg = approval_msg)


@app.route('/approve', methods=['POST'])
def approve_receipts():
    try:
        approved_ids = request.form.getlist('approvals')
        num_approvals = len(approved_ids)
        print("Approving receipts: " + str(approved_ids))
        
        connection = db_connect()
        with connection.cursor() as cursor:
            # Update records in receipts table
            sql = "UPDATE `receipts` WHERE `id`=%s SET `approved_by_id`=%s"
            cursor.executemany(sql, (approved_ids, session['user_id'],))
            print("Successfully updated approvals by " + str(session['user_id']) + " on the receipts table.")
    
            # Commit to save changes
            connection.commit()
            connection.close()
        
        
        approval_msg = str(num_approvals) + " receipts approved."
        return approvals(approval_msg)
    
    except BaseException as e:
        show_error = True
        print("Error in approve_receipts():", e) 
        return render_template('error.html', error_msg = e, show_error = show_error)
    


@app.route("/receipts")
def receipts():
    
    connection = db_connect()
    receipts = []
        
    try:    
        with connection.cursor() as cursor:
            # Fetch the most recent 20 records that are approved
            sql = "SELECT * FROM `receipts` WHERE `approved_by_id` IS NOT NULL ORDER BY `id` DESC LIMIT 20"
            cursor.execute(sql,)
            receipts = cursor.fetchall()
            
            # If a matching record exists, return result, otherwise return message.
            if len(receipts) == 0:
                print("Results array is empty. Something went wrong.")
            else:
                print("Returning receipts in array.")
                
    except BaseException as e:
        print("Error in receipts():", e)    
    
    # Don't show list of results if there aren't any.
    if len(receipts) > 0:
        show_results = True
    else:
        show_results = False
    
    return render_template('results_table.html', 
                             results = receipts,
                             num_receipts = len(receipts),
                             logged_in = session['logged_in'],
                             show_approvals = session['show_approvals'],
                             show_results = show_results)
        

@app.route("/receipts_json")
def receipts_json():
    # Return most recent 20 records in JSON.
    # This method exists to test the React UI.
    
    try:
        # Connect to database.
        connection = db_connect()
        receipts = []
        
        with connection.cursor() as cursor:
            # Read 20 records.
            sql = "SELECT * FROM `receipts` WHERE `approved_by_id` IS NOT NULL ORDER BY `id` DESC LIMIT 20"
            cursor.execute(sql,)
            receipts = cursor.fetchall()
            
            # If a matching record exists, return result, otherwise return message.
            if len(receipts) == 0:
                print("Results array is empty. Something went wrong.")
            else:
                print("Returning JSON.")
        
        for receipt in receipts:
            if "date_of_tweet" in receipt and receipt["date_of_tweet"] != None:
                receipt["date_of_tweet"] = receipt["date_of_tweet"].isoformat()
            if "date_added" in receipt and receipt["date_added"] != None:
                receipt["date_added"] = receipt["date_added"].isoformat()
        
        results = {}
        results["receipts"] = receipts
        
        return json.dumps(results, indent = 4, ensure_ascii = False)
                
    except BaseException as e:
        print("Error in receipts_json():", e)   
        return render_template('error.html', error_msg = e)


@app.route("/search/<string:name>/")
def search_user_url(name):
    print("Searching for user @" + name)
    return search_user(name)


@app.route('/search', methods=['POST'])
def search_user_form():
    user_searched = request.form['search_user']
    print("Searching for user @" + user_searched)
    return search_user(user_searched)


def search_user(user_searched):
    
    connection = db_connect()
    
    receipts = []
    show_error = False
    error_msg = ""
    username = user_searched
    
    if user_searched != None and user_searched != "":
        # Remove @ from username, if it exists.
        # If user entered a valid Twitter full or short URL, extract the username.
        try:
            username = parsing.parse_input_for_username(user_searched)
            show_search_name = True
            
            results = crud.search_receipts_for_user(username, connection, 20)
            receipts = results.receipts
            show_error = results.show_error
            error_msg = results.error_msg
                    
        except BaseException as e:
            print("Error in search_user():", e)
            error_msg = e
            show_error = True

    else: 
        show_search_name = False
       
        # Get most recent 20 receipts from db.
        try:
            with connection.cursor() as cursor:
                # Read 20 records
                sql = "SELECT * FROM `receipts` WHERE `approved_by_id` IS NOT NULL ORDER BY `id` DESC LIMIT 20"
                cursor.execute(sql,)
                receipts = cursor.fetchall()
                num_receipts = len(receipts)
                print("Displaying most recent 20 receipts.")
                    
        except BaseException as e:
            print("Error in search_user():", e)
            error_msg = e
            show_error = True
    
    # Don't show list of results if there aren't any.
    if receipts is None or len(receipts) == 0:
        show_results = False
        num_receipts = 0
    else:
        show_results = True
        num_receipts = len(receipts)
    
    return render_template('results_table.html', 
                             user_searched = user_searched,
                             username = username,
                             results = receipts,
                             num_receipts = num_receipts,
                             show_results = show_results,
                             show_error = show_error,
                             error_msg = error_msg,
                             show_search_name = show_search_name)
    

@app.route('/main')
def main():
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(session['key'], session['secret'])
    
    # This is used for testing, and may be removed later.
    userdata_json = session['userdata']
    
        
    return render_template('app.html', 
                                 logged_in = True,
                                 name = userdata_json['name'],
                                 followers_count = userdata_json['followers_count'])


#@app.route('/sturm', methods=['POST'])
#def sturm():
#    
#    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
#    auth.set_access_token(session['key'], session['secret'])
#    api_user = tweepy.API(auth)
#    
##    api_user = session['api']
#    user = request.form['screen_name']
#    num_receipts = request.form['num_receipts']
#    
#    # Set num_receipts to default 30 if not a number.
#    # TODO: Validate form before submit?
#    if num_receipts.isdigit():
#        num_receipts = int(num_receipts)
#    else:
#        num_receipts = 30
#        
#    # Remove @ from username, if it exists.
#    # TODO: add parsing to identify user from twitter.com URLs?
#    # TODO: Check if all status/user URLs begin with twitter.com/$screen_name.
#    # TODO: add error handling here if user enters bad URL
#    user = re.sub(r"@","",user)
#    
#    re_patterns = st.init(st.words)
#    st.set_api(api_user)
#    results = st.test_followers(user, re_patterns, num_receipts)
#    st.print_results(results.scores)
#    
#    # Don't show list of baddies if there aren't any.
#    if results.num_baddies > 0:
#        show_baddies = True
#    else:
#        show_baddies = False
#    
#    return flask.render_template('results.html', 
#                             user = user,
#                             baddies_names = results.baddies_names,
#                             baddies = results.baddies,
#                             results = results.scores,
#                             num_baddies = results.num_baddies,
#                             num_receipts = results.num_receipts,
#                             ratio = results.ratio,
#                             show_baddies = show_baddies,
#                             logged_in = True)


@app.route('/logout')
def logout():
    # remove variables from session
    del session['request_token']
    return redirect('../')


if __name__ == '__main__':
    app.debug = True
    app.run()