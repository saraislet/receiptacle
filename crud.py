# -*- coding: utf-8 -*-
"""
Created on Thu Nov  9 18:59:22 2017

@author: Sarai
"""

#import tweepy
#import pymysql.cursors

def search_receipts_for_user(username, connection, count = 20):
    # Retrieve up to $count records for username.
    results = Results([])
    
    try:
        with connection.cursor() as cursor:
            # Search database for username.
            # TODO: Look up username in accounts table, 
            #   update from Twitter if necessary,
            #   and search receipts table for twitter_id.
            sql = "SELECT id, twitter_id, blocklist_id, contents_text, url, screen_name, name, date_of_tweet"
            sql += " FROM `receipts`"
            sql += " WHERE `screen_name`=%s AND `approved_by_id` IS NOT NULL"
            sql += " ORDER BY `id` DESC LIMIT 20"
            cursor.execute(sql, (username,))
            receipts = cursor.fetchall()

            # If a matching record exists, return result, otherwise return message.
            if results.receipts == None:
                results.show_error = True
                results.error_msg = "User searched is not in the database."
                print(results.error_msg)
            else:
                results.receipts = receipts
                print("User searched is in the database.")
            
            return results
        
    except BaseException as e:
            print("Error in search_user():", e)
            results.show_error = True
            return results


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
        self.num_receipts = len(receipts)
        self.show_error = False
        self.error_msg = ""