# -*- coding: utf-8 -*-
"""
Created on Tue Sep 12 20:12:44 2017

@author: Sarai
"""

import os
from flask import Flask, request, render_template, redirect, session
import tweepy
import crud, sign_in
#import Sturmtest as st

app = Flask(__name__)
app.secret_key = os.environ['session_secret_key']

consumer_key = os.environ['consumer_key']
consumer_secret = os.environ['consumer_secret']


@app.route('/')
def send_token():
    return sign_in.send_token()


@app.route("/verify")
def get_verification():
    return sign_in.get_verification()


@app.route("/approve")
def approvals(approval_msg=""):
    return crud.get_approvals(approval_msg)


@app.route('/approve', methods=['POST'])
def approve_receipts():
    # Get values from post request, and update indicated approvals in db.
    try:
        approved_ids = request.form.getlist('approvals')
        for n in approved_ids:
            if n.isdigit():
                n = int(n)
            else:
                raise ValueError("Item in array is not an integer: " + str(n))
        
        return crud.post_approvals(approved_ids)
    
    except BaseException as e:
        print("Error in approve_receipts():", e)   
        return render_template('error.html', error_msg = e)


@app.route("/receipts")
def receipts():
    return crud.get_receipts()
        

@app.route("/receipts_json")
def receipts_json():
    return crud.get_receipts_json()


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
    return crud.search_receipts_for_user(user_searched)
    

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

@app.route('/logout')
def logout():
    # remove variables from session
    if 'request_token' in session:
        del session['request_token']
    if 'logged_in' in session:
        del session['logged_in']
    if 'show_approvals' in session:
        del session['show_approvals']
    return redirect('../')


if __name__ == '__main__':
    app.debug = True
    app.run()