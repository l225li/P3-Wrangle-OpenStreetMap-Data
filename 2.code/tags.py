#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import pprint
import re
from collections import defaultdict
"""
Your task is to explore the data a bit more.
Before you process the data and add it into your database, you should check the
"k" value for each "<tag>" and see if there are any potential problems.

We have provided you with 3 regular expressions to check for certain patterns
in the tags. As we saw in the quiz earlier, we would like to change the data
model and expand the "addr:street" type of keys to a dictionary like this:
{"address": {"street": "Some value"}}
So, we have to see if we have such tags, and if we have any tags with
problematic characters.

Please complete the function 'key_type', such that we have a count of each of
four tag categories in a dictionary:
  "lower", for tags that contain only lowercase letters and are valid,
  "lower_colon", for otherwise valid tags with a colon in their names,
  "problemchars", for tags with problematic characters, and
  "other", for other tags that do not fall into the other three categories.
See the 'process_map' and 'test' functions for examples of the expected format.
"""


lower = re.compile(r'^([a-z]|_)*$')
lower_digit = re.compile(r'^([a-z0-9]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
lower_two_colons = re.compile(r'^([a-z]|_)*:([a-z]|_)*:([a-z]|_)*$')
lower_three_colons = re.compile(r'^([a-z]|_)*:([a-z]|_)*:([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
other_tags = defaultdict(int)
weird_set = set()
def key_type(element, keys):
    
    if element.tag == "tag":
        key = element.attrib['k']
        value = element.attrib['v']
        if problemchars.search(key):
            keys['problemchars'] += 1
        elif key == "FIXME":
            keys['FIXME'] += 1
        elif lower_colon.search(key):
            keys['lower_colon'] += 1
            
        elif lower_two_colons.search(key):
            keys['lower_two_colons'] += 1
            
        elif lower_three_colons.search(key):
            keys['lower_three_colons'] += 1
            
        elif lower.search(key):
            keys['lower'] += 1
            weird_set.add(key)
        elif lower_digit.search(key):
            keys['lower_digit'] += 1

        else:
            keys['other'] += 1
            other_tags[key] += 1
    return keys



def process_map(filename):
    keys = {"lower": 0,"FIXME": 0, "lower_colon": 0, "lower_two_colons": 0, "lower_three_colons": 0,"lower_digit": 0, "problemchars": 0, "other": 0}
    for _, element in ET.iterparse(filename):
        keys = key_type(element, keys)
    return keys


def test():
    keys = process_map('../4.richmondhill_sample.osm')
    print "====================Tag Types Count===================="
    pprint.pprint(keys)
    print "======================Other Tags======================"
    print other_tags
    print "======================Interested group of tags======================"
    print sorted(weird_set)

if __name__ == "__main__":
    test()