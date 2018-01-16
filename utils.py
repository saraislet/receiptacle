# -*- coding: utf-8 -*-
"""
Created on Mon Nov 27 10:29:25 2017

@author: Sarai
"""

import os
import pymysql
import tweepy
from flask import session

consumer_key = os.environ['consumer_key']
consumer_secret = os.environ['consumer_secret']

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
        print('Error in get_api(): Failed to build OAuthHandler!')
        raise OSError("Cannot connect to Twitter API.")
        return


def get_user_api(twitter_id):
    # Rebuild OAuthHandler and return tweepy.API(auth) if session exists.
    # Otherwise, return error_msg.
    
    try:
        # Fetch key and secret
        connection = db_connect()
        
        with connection.cursor() as cursor:
            # Read a single record
            sql = "SELECT `screen_name`, `twitter_id`,"
            sql += " `oauth_key`, `oauth_secret`"
            sql += " FROM `users`"
            sql += " WHERE twitter_id = %s"
            cursor.execute(sql, (twitter_id,))
            result = cursor.fetchone()
        connection.close()
        
        # Build OAuthHandler
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(result['oauth_key'], result['oauth_secret'])
        return tweepy.API(auth)
    except tweepy.TweepError:
        print('Error in get_user_api(): Failed to build OAuthHandler!')
        raise OSError("Cannot connect to Twitter API.")
        return