# -*- coding: utf-8 -*-
"""
Created on Tue Sep 12 20:12:44 2017

@author: Sarai
"""

import os, json
from flask import Flask, request, render_template, redirect, session
import tweepy
import pymysql.cursors
import parsing
#import Sturmtest as st

app = Flask(__name__)

consumer_key = os.environ['consumer_key']
consumer_secret = os.environ['consumer_secret']

callback_url = ''


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


@app.route('/')
def temporary_redirect():
    # Until the rest of the app is built, redirect to receipts.
    return redirect("/receipts", code=302)


#@app.route('/')
#def send_token():
#    redirect_url = ""
#    auth = tweepy.OAuthHandler(consumer_key, consumer_secret, callback_url)
##    redirect_url = auth.get_authorization_url()
#
#    try: 
#        #get the request tokens
#        redirect_url= auth.get_authorization_url()
#        session['request_token'] = auth.request_token
#        
#        return render_template('start.html', redirect_url = redirect_url)
#    except tweepy.TweepError:
#        error_msg = 'Error! Failed to get request token'
#        print(error_msg)
#        
#        # TODO: Ideally, this would return an error message. Test this.
#        return flask.render_template('error.html',
#                                     error_msg = error_msg)
#
#
#@app.route("/verify")
#def get_verification():
#    # Get the verifier key from the request url.
#    verifier = request.args['oauth_verifier']
#
#    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
#    print("session dict object is: " + str(session))
#    token = session['request_token']
#    del session['request_token']
#
#    auth.request_token = token
#
#    try:
#        auth.get_access_token(verifier)
#        global api_user
#        api_user = tweepy.API(auth)
#        userdata = api_user.me()
#        
#        # Store key and secret in session.
#        # get_api() rebuilds OAuthHandler and returns tweepy.API(auth)
#        session['key'] = auth.access_token
#        session['secret'] = auth.access_token_secret
#        session['userdata'] = userdata.__getstate__()['_json']
#        
#        return flask.render_template('app.html', 
#                                 name = userdata.name, 
#                                 screen_name = userdata.screen_name, 
#                                 bg_color = userdata.profile_background_color, 
#                                 followers_count = userdata.followers_count, 
#                                 created_at = userdata.created_at,
#                                 logged_in = True)
#        
#    except tweepy.TweepError:
#        error_msg = 'Error! Failed to get access token.'
#        print(error_msg)
#        
#        return flask.render_template('error.html',
#                                     error_msg = error_msg)


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
    
    
    
#    print(receipts.("utf-8"))
#    results = {}
#    results["receipts"] = receipts
#    return json.dumps(results, ensure_ascii = False)
    
    return render_template('results_table.html', 
                             results = receipts,
                             num_results = len(receipts),
                             show_results = show_results)
        

@app.route("/receipts_json")
def receipts_json():
    
    
    try:
        # Connect to database.
        connection = db_connect()
        receipts = []
        
        with connection.cursor() as cursor:
            # Read 20 records.
            sql = "SELECT * FROM `receipts` LIMIT 20"
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
        return render_template('error.html',
                                     error_msg = e)


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
#    user_searched = request.form['search_user']
#    print("Searching for user @" + user_searched)
    
    receipts = []
    show_error = False
    error_msg = ""
    username = user_searched
    
    if user_searched != None and user_searched != "":
        # Remove @ from username, if it exists.
        # If user entered a valid Twitter full or short URL, extract the username.
        # TODO: add error handling here if user enters bad URL
        try:
            username = parsing.parse_input_for_username(user_searched)
        except BaseException as e:
            print("Error in search_user():", e)
            error_msg = e
            show_error = True

        show_search_name = True
        
        try:    
            with connection.cursor() as cursor:
                # Read a single record
                sql = "SELECT * FROM `receipts` WHERE `screen_name`=%s AND `approved_by_id` IS NOT NULL ORDER BY `id` DESC LIMIT 20"
                cursor.execute(sql, (username,))
                receipts = cursor.fetchall()

                # If a matching record exists, return result, otherwise return message.
                if len(receipts) == 0:
                    error_msg = "User searched is not in the database."
                    print(error_msg)
                    show_error = True
                else:
                    print("User searched is in the database.")
                    #TODO: Display number of receipts found.
                    
        except BaseException as e:
            print("Error in search_user():", e)

    else: 
        show_search_name = False
       
        # Get most recent 20 receipts from db.
        receipts = []
        try:
            with connection.cursor() as cursor:
                # Read 20 records
                sql = "SELECT * FROM `receipts` WHERE `approved_by_id` IS NOT NULL ORDER BY `id` DESC LIMIT 20"
                cursor.execute(sql,)
                receipts = cursor.fetchall()
                print("Displaying most recent 20 receipts.")
                    
        except BaseException as e:
            print("Error in search_user():", e)
            error_msg = e
            show_error = True
    
    # Don't show list of results if there aren't any.
    if len(receipts) > 0:
        show_results = True
    else:
        show_results = False
    
    return render_template('results_table.html', 
                             user_searched = user_searched,
                             username = username,
                             results = receipts,
                             num_results = len(receipts),
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
#    num_results = request.form['num_results']
#    
#    # Set num_results to default 30 if not a number.
#    # TODO: Validate form before submit?
#    if num_results.isdigit():
#        num_results = int(num_results)
#    else:
#        num_results = 30
#        
#    # Remove @ from username, if it exists.
#    # TODO: add parsing to identify user from twitter.com URLs?
#    # TODO: Check if all status/user URLs begin with twitter.com/$screen_name.
#    # TODO: add error handling here if user enters bad URL
#    user = re.sub(r"@","",user)
#    
#    re_patterns = st.init(st.words)
#    st.set_api(api_user)
#    results = st.test_followers(user, re_patterns, num_results)
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
#                             num_results = results.num_results,
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
    app.secret_key = '\n\x8d-\xd1"\xfa;EG`\xc1?|\xd5*\xeaO\x91\x0c\x0c\x1as\x1e<'
#    app.config['SESSION_TYPE'] = 'filesystem'
    app.run()
    
# TODO: put a new random string in .env and update heroku env