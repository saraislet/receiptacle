# -*- coding: utf-8 -*-
"""
Created on Thu Nov  9 18:59:22 2017

@author: Sarai
"""

#import tweepy
#import pymysql.cursors

import json, datetime
from flask import redirect, render_template, session
import parsing, utils

select_columns_from_receipts = "SELECT id, receipts.twitter_id, blocklist_id"
select_columns_from_receipts += ", contents_text, url, status_id"
select_columns_from_receipts += ", receipts.screen_name, receipts.name"
select_columns_from_receipts += ", date_of_tweet"
select_columns_from_receipts += ", users.screen_name AS blocklist_name"
select_columns_from_receipts += " FROM `receipts`"
select_columns_from_receipts += " LEFT JOIN users ON receipts.blocklist_id = users.twitter_id"


def check_admins(user_id, connection):
    # Check if authenticated user is a blocklist admin, return array of blocklist_ids.
    
    try:        
        with connection.cursor() as cursor:
            sql = "SELECT blocklist_id FROM `blocklist_admins`"
            sql += " WHERE `admin_id`=%s"
            cursor.execute(sql, (user_id,))
            blocklist_ids = cursor.fetchall()
            
            if blocklist_ids is None:
                return []
            else:
                # Get blocklist_id value from each item in blocklist_ids.
                blocklist_ids = [item['blocklist_id'] for item in blocklist_ids]
                output = "User_id " + str(user_id)
                output +=" is blocklist admin for the following: "
                output += str(blocklist_ids)
                print(output)
                return blocklist_ids
    except BaseException as e:
        print("Error in check_admins():", e)
        return []
    

def check_user(twitter_id, connection, api, key="", secret=""):
    # Test if user is in the database ,then insert or update if necessary.    
    try:    
        with connection.cursor() as cursor:
            # Read a single record
            sql = "SELECT `twitter_id` FROM `users`"
            sql += " WHERE `twitter_id`=%s LIMIT 1"
            cursor.execute(sql, (twitter_id,))
            result = cursor.fetchone()
            
            # If a matching record exists, return true, otherwise return false.
            if result == None:
                print("User is not in the database. Inserting new row.")
                insert_user(twitter_id, connection, api, key, secret)
            else:
                print("User is in the database. Checking for updates.")
                update_user(twitter_id, connection, api, key, secret)
            return
                
    except BaseException as e:
        print("Error in check_user()", e)
        return


def insert_user(twitter_id, connection, api, key, secret):
    # Pull user details from API and insert into users table.
    userdata = api.get_user(twitter_id)
    name = userdata.name
    screen_name = userdata.screen_name
    
    try:
        with connection.cursor() as cursor:
            # Create a new record in users table
            sql = "INSERT INTO `users`"
            sql += " (`twitter_id`, `name`, `screen_name`, `oauth_key`,"
            sql += " `oauth_secret`, `date_updated`) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, (twitter_id, name, screen_name, key, secret, datetime.datetime.now(),))
        
            # Commit to save changes
            connection.commit()
    
            print("Successfully inserted @" + screen_name + " into users table.")
            return

    except BaseException as e:
        print("Error in insert_user()", e)
        return

def update_user(twitter_id, connection, api, key, secret):
    # Test if user should be updated, and update if necessary.
    try:
        with connection.cursor() as cursor:
            # Read a single record
            sql = "SELECT `date_updated` FROM `users`"
            sql += " WHERE `twitter_id`=%s LIMIT 1"
            cursor.execute(sql, (twitter_id,))
            result = cursor.fetchone()
            date_updated = result['date_updated']
            
            # If difference between now() and date_updated is more than 1 day, update
            if (datetime.datetime.now().timestamp() - date_updated.timestamp())/60/60/24 > 1:
                print("User is out of date. Updating user.")
                userdata = api.get_user(twitter_id)
                name = userdata.name
                screen_name = userdata.screen_name
                
                with connection.cursor() as cursor:
                    # Update a record in users table
                    sql = "UPDATE `users` WHERE `twitter_id`=%s LIMIT 1"
                    sql += " SET `name`=%s, `screen_name`=%s,"
                    sql += " `oauth_key`=%s, `oauth_secret`=%s, `date_updated`=%s"
                    cursor.execute(sql, (twitter_id, name, screen_name, key, secret, datetime.datetime.now(),))
                    print("Successfully updated @" + screen_name + " from users table.")
        
                # Commit to save changes
                connection.commit()
            else:
                print("User is up to date.")
        return
    
    except BaseException as e:
        print("Error in update_user()", e)
        return
    

def get_approvals(approval_msg="", args={}):
    # Get the most recent 20 approvals.
    
    connection = utils.db_connect()
    results = Results([])
    results.approval_msg = approval_msg
        
    try:
        # Ensure the user is logged in, and if not, redirect to login page.
        # TODO: Consider using Flask decorators and flask.ext.login.login_required
        if 'logged_in' not in session:
            return redirect("/", code=302)
        elif 'user_id' in session:
            blocklist_ids = check_admins(session['user_id'], connection)
        else:
            return redirect("/login", code=302)
        
        with connection.cursor() as cursor:
            # Fetch the most recent 20 records that are not approved
            sql = select_columns_from_receipts
            sql += " WHERE `approved_by_id` IS NULL"
            sql += " AND `blocklist_id` in %s"
            sql += " ORDER BY `id` DESC LIMIT 20"
            cursor.execute(sql, (tuple(blocklist_ids),))
            results.extend(cursor.fetchall())
                
    except BaseException as e:
        results.show_error = True
        results.error_msg = e
        print("Error in approve():", e)  
    
    finally:
        connection.close()
    
    # Don't show list of results if there aren't any.
    if len(results.receipts) > 0:
        results.show_results = True
        print("Returning approval receipts in array.")
    else:
        results.show_results = False
        print("Approval results array is empty. Something went wrong.")
        
    if approval_msg is not "":
        results.show_approval_msg = True
    else:
        results.show_approval_msg = False
    
    return render_template('approvals.html', results = results,
                             logged_in = session.get('logged_in', False),
                             show_approvals = session.get('show_approvals', False))


def post_approvals(approved_ids=[]):
    # Update indicated approvals in db.
    try:
        num_approvals = len(approved_ids)
        print("Approving receipts: " + str(approved_ids))
        
        connection = utils.db_connect()
        with connection.cursor() as cursor:
            # Update records in receipts table
            for approved_id in approved_ids:
                sql = "UPDATE `receipts` SET `approved_by_id`=%s WHERE `id`=%s"
                cursor.execute(sql, (session['user_id'], approved_id,))
            print("Successfully updated approvals by " + str(session['user_id']) + " on the receipts table.")
    
            # Commit to save changes
            connection.commit()
            connection.close()
        
        if num_approvals == 1:
            approval_msg = "1 receipt approved."
        elif num_approvals > 1:
            approval_msg = str(num_approvals) + " receipts approved."
            
        return get_approvals(approval_msg, {})
    
    except BaseException as e:
        show_error = True
        print("Error in approve_receipts():", e) 
        return render_template('error.html', error_msg = e, show_error = show_error,
                             logged_in = session.get('logged_in', False),
                             show_approvals = session.get('show_approvals', False))


def get_receipts(args):
    # Return the most recent 20 approved receipts.
    connection = utils.db_connect()
    results = Results([])
        
    try:    
        with connection.cursor() as cursor:
            # Fetch the most recent 20 records that are approved
            sql = select_columns_from_receipts
            sql += " WHERE `approved_by_id` IS NOT NULL"
            sql += " ORDER BY `id` DESC LIMIT 20"
            cursor.execute(sql,)
            receipts = cursor.fetchall()
            
            # If a matching record exists, return result, otherwise return message.
            if receipts is None:
                print("Results array is empty. Something went wrong.")
            else:
                results.set(receipts)
                print("Returning receipts in array.")
                
    except BaseException as e:
        print("Error in get_receipts():", e)    
    
    # Don't show list of results if there aren't any.
    if results.num_receipts > 0:
        results.show_results = True
    else:
        results.show_results = False
    
    return render_template('results_table.html', results=results,
                             logged_in = session.get('logged_in', False),
                             show_approvals = session.get('show_approvals', False))


def get_receipts_json(args):
    # Return most recent 20 records in JSON.
    # This method exists to test the React UI.
    
    try:
        # Connect to database.
        connection = utils.db_connect()
        receipts = []
        
        with connection.cursor() as cursor:
            # Read 20 records.
            sql = "SELECT * FROM `receipts` WHERE `approved_by_id` IS NOT NULL"
            sql += " ORDER BY `id` DESC LIMIT 20"
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
        return render_template('error.html', error_msg = e,
                             logged_in = session.get('logged_in', False),
                             show_approvals = session.get('show_approvals', False))


def search_receipts_for_user(user_searched, args):
    # Return most recent 20 receipts matching user_searched.
    # Retrieve up to $count records for username.
    results = Results([])
    connection = utils.db_connect()
    
    show_all = args.get('show_all', 'False').lower()
    
    username = user_searched
    
    if user_searched != None and user_searched != "":
        # Remove @ from username, if it exists.
        # If user entered a valid Twitter full or short URL, extract the username.
        try:
            username = parsing.parse_input_for_username(user_searched)
            results.show_search_name = True
            
            with connection.cursor() as cursor:
                # Search database for username.
                # TODO: Look up username in accounts table, 
                #   update from Twitter if necessary,
                #   and search receipts table for twitter_id.
                sql = select_columns_from_receipts
                sql += " WHERE receipts.screen_name=%s"
                
                # Only show all receipts if that request parameter is True
                if show_all != "true":
                    sql += " AND receipts.approved_by_id IS NOT NULL"
                
                sql += " ORDER BY `id` DESC LIMIT 20"
                cursor.execute(sql, (username,))
                receipts = cursor.fetchall()
    
                # If a matching record exists, return result, otherwise return message.
                if receipts == None or receipts == ():
                    results.show_error = True
                    results.show_results = False
                    results.error_msg = "User searched is not in the database."
                    print(results.error_msg)
                else:
                    results.show_results = True
                    results.set(receipts)
                    print("User searched is in the database.")
                    
        except BaseException as e:
            print("Error in search_receipts_for_user():", e)
            results.error_msg = e
            results.show_error = True

    else: 
        results.show_search_name = False
       
        # Get most recent 20 receipts from db.
        try:
            with connection.cursor() as cursor:
                # Read 20 records
                sql = select_columns_from_receipts 
                sql += " WHERE `receipts.approved_by_id` IS NOT NULL ORDER BY `id` DESC LIMIT 20"
                cursor.execute(sql,)
                receipts = cursor.fetchall()
                print("Displaying most recent 20 receipts.")
                
                # If a matching record exists, return result, otherwise return message.
                if receipts is None:
                    results.show_results = False
                    print("Results array is empty. Something went wrong.")
                else:
                    results.show_results = True
                    results.set(receipts)
                    print("Returning receipts in array.")
                    
        except BaseException as e:
            print("Error in search_receipts_for_user():", e)
            results.error_msg = e
            results.show_error = True
    
    return render_template('results_table.html', results = results,
                           username = username,
                           logged_in = session.get('logged_in', False),
                           show_approvals = session.get('show_approvals', False))


class Results(object):
    """
    Results contain attributes and basic methods:
        
    Attributes:
        receipts: list of receipts
        num_receipts: integer number of receipts found
        show_error: indicates to the front-end that it should display error_msg
    """
    
    def __init__(self, receipts):
        # Create a Results object with receipts array and default values for attributes.
        self.receipts = receipts
        self.num_receipts = len(self.receipts)
        self.show_approvals = False
        self.show_error = False
        self.show_results = False
        self.show_search_name = False
        self.approval_msg = ""
        self.error_msg = ""
        self.logged_in = False
        
    def set(self, receipts):
        self.receipts = receipts
        self.num_receipts = len(self.receipts)

    def extend(self, receipts):
        self.receipts.extend(receipts)
        self.num_receipts = len(self.receipts)