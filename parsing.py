# -*- coding: utf-8 -*-
"""
Created on Sun Nov  5 10:59:27 2017

@author: Sarai
"""

import re, requests


def unshorten_url_re(url):
    # Return expanded URL from regex matches.
    # Unclear how to combine this with previous function nontrivially.
    # This works for now.
    if url == None:
        return None
    else:
        return requests.head(url.group(), allow_redirects=True).url


def unshorten_urls_in_text(string):
    # Unshorten all URLs in a string.
    return re.sub(r'(https?://\S*)', unshorten_url_re, string)


def remove_leading_ats(tweet):
    # Remove any leading @s (e.g., replies) from a tweet.
    # Any @ that is not at the beginning of a tweet will be left.
    return re.sub(r'^(@[a-zA-Z0-9_]{1,15})', "", tweet)

def remove_ats(tweet):
    # Remove all @s (e.g., replies) from a tweet.
    return re.sub(r'(@[a-zA-Z0-9_]{1,15})', "", tweet)


def get_twitter_urls(text):
    # Check text for twitter.com or t.co shortlink, and return all matches or an empty string.
    text = unshorten_urls_in_text(text)
    
    # url = re.sub(r'.*(https://twitter\.com/[a-zA-Z0-9_]{1,15}/status/\d+)|(https://t.co/[\w]{1,20}).*', r'\1', url)
    #matches = re.findall(r'.*(https://twitter\.com/[a-zA-Z0-9_]{1,15}/status/\d+).*', text)
    matches = re.findall(r'(https://twitter\.com/[a-zA-Z0-9_]{1,15}/status/\d+)', text)

    if matches != None:
        return matches
    else:
        return ""


def verify_twitter_url(url):
    # Verify that a URL has a Twitter domain
    match = re.match(r'https://twitter\.com/.+', url)
    
    if match != None:
        return True
    else:
        return False


def verify_twitter_status_url(url):
    # Verify that a URL belongs to a Twitter status
    match = re.match(r'https://twitter\.com/[a-zA-Z0-9_]{1,15}/status/\d+', url)
    
    if match != None:
        return True
    else:
        return False


def get_tweet_from_url(url, api):
    # Match ID from Twitter status URL and return status object.   
    status_id = re.sub(r'https://twitter\.com/[a-zA-Z0-9_]{1,15}/status/(\d+).*', r'\1', url)
    
    # Extended tweet mode returns full text without truncation.
    return api.get_status(status_id, tweet_mode='extended')


def get_twitter_name_from_url(url):
    # Match username from Twitter URL
    match = re.match(r'https://twitter\.com/([a-zA-Z0-9_]{1,15})[/|\s]?.*', url)
    
    if match == None or match == "":
        raise ValueError("Unable to identify username.")
    else:
        return match.group(1)


def get_twitter_id_from_url(url, api):
    # Get username from URL, then fetch ID from Twitter API.
    username = get_twitter_name_from_url(url)    
    return api.get_user(username).id


def parse_username_from_text(text):
    # Remove leading space or leading @, return first word
    match = re.match(r'\s?@?(\w+)', text)
    
    if match != None:
        return match.group(1)
    else:
        return ""


def get_username_from_text(text):
    # Remove leading space or leading @, ensure there are only 15 characters
    username = parse_username_from_text(text)
    
    if username == None or username == "":
        raise ValueError("Unable to identify username.")
    elif len(username) > 15:
        raise ValueError("Username must have 15 characters or less.")
    else:
        return username


def parse_input_for_username(text):
    # If there is a Twitter URL, parse the screen_name.
    # Else, remove @ if it exists and return the following username
    urls = get_twitter_urls(text)
    
    if urls != "" and urls != []:
        username = get_twitter_name_from_url(urls[0])
    else:
        username = get_username_from_text(text)
    
    return username