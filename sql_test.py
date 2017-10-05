# -*- coding: utf-8 -*-
"""
Created on Wed Oct  4 14:44:39 2017

@author: Sarai
"""

import pymysql.cursors
import config_local as config  


# Connect to the database
connection = pymysql.connect(host = config.host,
                             user = config.user,
                             password = config.password,
                             db = config.database,
                             charset = 'utf8mb4',
                             cursorclass = pymysql.cursors.DictCursor)

try:
    with connection.cursor() as cursor:
        # Create a new record
        sql = "INSERT INTO `users` (`twitter_id`, `oauth_key`, `oauth_secret`) VALUES (%s, %s, %s)"
        cursor.execute(sql, ('369', 'key', 'secret'))

    # Ccommit to save changes
    connection.commit()

    with connection.cursor() as cursor:
        # Read a single record
        sql = "SELECT `twitter_id`, `oauth_key`, `oauth_secret` FROM `users` WHERE `twitter_id`=%s"
        cursor.execute(sql, ('369',))
        result = cursor.fetchone()
        print(result)
finally:
    connection.close()