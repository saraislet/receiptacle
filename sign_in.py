# -*- coding: utf-8 -*-
"""
Created on Mon Nov 27 10:02:22 2017

@author: Sarai
"""

import os
from flask import redirect, render_template, request, session
import tweepy
import crud, utils

consumer_key = os.environ['consumer_key']
consumer_secret = os.environ['consumer_secret']

#hostname = 'http://127.0.0.1:5000'
#hostname = 'https://young-meadow-72614.herokuapp.com'
hostname = 'https://www.receiptacle.com'
callback_url = hostname + '/verify'


def send_token():
    redirect_url = ""
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret, callback_url)

    try: 
        #get the request tokens
        redirect_url = auth.get_authorization_url()
        session['request_token'] = auth.request_token
        
        return render_template('start.html', redirect_url = redirect_url)
    
    except tweepy.TweepError:
        error_msg = 'Error! Failed to get request token'
        print(error_msg)
        
        return render_template('error.html', error_msg = error_msg)
    
def get_verification():
    # Get the verifier key from the request url.
    try:
        verifier = request.args['oauth_verifier']
    
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        token = session['request_token']
        del session['request_token']
    
        auth.request_token = token
        
    except KeyError as e:
        print("KeyError setting up get_verification(): ", e)
        return render_template('error.html', error_msg = e)
    
    except BaseException as e:
        print("Error in get_verification():", e)
        return render_template('error.html', error_msg = e)
        

    try:
        auth.get_access_token(verifier)
        api = tweepy.API(auth)
        connection = utils.db_connect()
        
        twitter_id = api.me().id
        
        crud.check_user(twitter_id, connection, api, key=auth.access_token, secret=auth.access_token_secret)
        
        # Store key and secret in session.
        # get_api() rebuilds OAuthHandler and returns tweepy.API(auth)
        session['key'] = auth.access_token
        session['secret'] = auth.access_token_secret
        session['logged_in'] = True
        session['user_id'] = twitter_id
        session['blocklist_ids'] = crud.check_admins(session['user_id'], connection)
        
        if session['blocklist_ids'] is not []:
            session['show_approvals'] = True
        
        return redirect("/receipts", code=302)
        
    except tweepy.TweepError:
        error_msg = 'Error! Failed to get access token.'
        print(error_msg)
        
        return render_template('error.html', error_msg = error_msg)
    
    except BaseException as e:
        print("Error in get_verification():", e)
        return render_template('error.html', error_msg = e)
    
    finally:
        connection.close()