# -*- coding: utf-8 -*-
"""
Created on Sun Dec  3 17:24:42 2017

@author: Sarai
"""

import unittest
import parsing


class TestStringMethods(unittest.TestCase):
    
    def setUp(self):
        self.strings = []
        self.strings.append("@alice")#0
        self.strings.append("@alice hi")#1
        self.strings.append("hi @alice")#2
        self.strings.append("@alice say hi to @bob")#3
        self.strings.append("https://twitter.com/fail/user/status/912730953935552512")#4
        self.strings.append("https://twitter.com/fail_name_too_long/912730953935552512")#5
        self.strings.append("https://twitter.com/fail/")#6
        self.strings.append("https://example.com/fail_domain/")#7
        self.strings.append("https://t.co/DQks3TCgrd")#8
        self.strings.append("@alice see https://twitter.com/saraislet/status/912730953935552512")#9
        self.strings.append("https://t.co/DQks3TCgrd see this site")#10
        self.strings.append("@alice go to https://t.co/DQks3TCgrd for more info")#11

    def test_remove_ats(self):
        self.assertEqual(parsing.remove_ats(self.strings[0]), "")
        self.assertEqual(parsing.remove_ats(self.strings[1]), " hi")
        self.assertEqual(parsing.remove_ats(self.strings[2]), "hi ")
        self.assertEqual(parsing.remove_ats(self.strings[3]), " say hi to ")

    def test_remove_leading_ats(self):
        self.assertEqual(parsing.remove_leading_ats(self.strings[0]), "")
        self.assertEqual(parsing.remove_leading_ats(self.strings[1]), " hi")
        self.assertEqual(parsing.remove_leading_ats(self.strings[2]), "hi @alice")
        self.assertEqual(parsing.remove_leading_ats(self.strings[3]), " say hi to @bob")
        
    def test_get_twitter_urls(self):
        self.assertEqual(parsing.get_twitter_urls(self.strings[0]), [])
        self.assertEqual(parsing.get_twitter_urls(self.strings[4]), [])
        self.assertEqual(parsing.get_twitter_urls(self.strings[5]), [])
        self.assertEqual(parsing.get_twitter_urls(self.strings[6]), [])
        self.assertEqual(parsing.get_twitter_urls(self.strings[7]), [])
        self.assertEqual(parsing.get_twitter_urls(self.strings[8]), ["https://twitter.com/saraislet/status/911661465752371201"])
        self.assertEqual(parsing.get_twitter_urls(self.strings[9]), ["https://twitter.com/saraislet/status/912730953935552512"])
        self.assertEqual(parsing.get_twitter_urls(self.strings[10]), ["https://twitter.com/saraislet/status/911661465752371201"])
        self.assertEqual(parsing.get_twitter_urls(self.strings[11]), ["https://twitter.com/saraislet/status/911661465752371201"])
        

if __name__ == '__main__':
    unittest.main()