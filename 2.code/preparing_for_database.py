#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Prepare the OSMFILE (XML) to JSON format in order to import into MongoDB

Examples:
    $ python preparing_for_database.py

    Result:    
    '4.richmondhill_sample.osm.json' is created in the current directory
    
    Uses:
    # Start mongoDB
    $ mongod
    # import to database test as collection osm
    $ mongoimport --db test --collection osm --file 4.richmondhill_sample.osm.json

"""
import xml.etree.cElementTree as ET
import pprint
import re
import codecs
import json
from collections import defaultdict
from audit import is_street_name, is_post_code, update_name, update_postcode


OSMFILE = '../4.richmondhill_sample.osm'
lower = re.compile(r'^([a-z]|_)*$')
lower_digit = re.compile(r'^([a-z0-9]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
addr = re.compile(r'^addr:([a-z]+)$')
CREATED = [ "version", "changeset", "timestamp", "user", "uid"]
duplist = ["colour", "name", "atm", "building", "source", "destination", "lanes", 
           "railway","maxspeed","opening_hours","hov","internet_access","phone",
           "aerialway","capacity"]
weird_set = set() # tag keys that are ignored by shape_element 

def shape_element(element):
    """Shape the XML Element into python dictionary format 
    which later on could be easily translated into JSON Document
    * Only shapes the Elements that represents "node" or "way" * 

    Args:
        element (Element): xml Element to be shaped 

    Returns:
        node ({}): dictionary format of element, None if Element
                   doesn't represent "node" or "way"
    """
    node = {}
    if element.tag == "node" or element.tag == "way" :
        node['type'] = element.tag
        node['created'] = {}

        for attrib in element.attrib.keys():
            if attrib in CREATED:
                node['created'][attrib] = element.attrib[attrib]
            elif attrib not in ['lat', 'lon']:
                node[attrib] = element.attrib[attrib]
        try:
            node['pos'] = [float(element.attrib['lat']), float(element.attrib['lon'])]
            #print node['pos']
        except:
            pass
        # address
        for tag in element.iter("tag"):
            key = tag.attrib['k']
            value = tag.attrib['v']
            if not problemchars.search(key):
                m1 = addr.search(key)
                m2 = lower_colon.search(key)
                m3 = lower.search(key)
                m4 = lower_digit.search(key)
                if m1:
                    key_in_address = m1.group(1)
                    if 'address' not in node.keys():
                        node['address'] = {}
                    if is_street_name(tag):
                        value = update_name(value)
                    if is_post_code(tag):
                        value = update_postcode(value)
                    if value:
                        node['address'][key_in_address] = value
                    #print "address:%s : %s"%(k, value)
                elif m2:
                    k1, k2= m2.group().split(':')
                    if k1 not in duplist:
                        if k1 not in node.keys():
                            node[k1] = {}
                        #print "%s:%s : %s"%(k1, k2, value)
                        node[k1][k2] = value
                elif m3:
                    node[key] = value
                elif m4: 
                    k = m4.group()
                    k = k.translate(None, "_1")
                    node[k] = value
                elif key.startswith("geobase:") or key.startswith("addr:"):
                    k1, k2 = key.split(":")
                    if k1 not in node.keys():
                        node[k1] = {}
                    if lower_digit.search(k2):
                        k2 = k2.translate(None, "_1")
                    node[k1][k2] = value 
                else: 
                    weird_set.add(key)
        if element.tag == "way" and element.iter("nd"):
            key = "node_refs"
            node[key] = []
            for tag in element.iter("nd"):
                value = tag.attrib['ref']
                node[key].append(value)

        return node
    else:
        return None


def process_map(file_in, pretty = False):
    """Process file_in(XML) into JSON format and write it into file_out
    
    Args:
        file_in (str): location of the XML file
        pretty (bool): pretty print or not for the file_out (False would cause a smaller file)

    Returns:
        data ([]): list of elements translated in dictionaries
        
    """
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data

def test():
    # with open('example.osm.xml', 'r') as f:
    #   pprint.pprint(f.read())
    data = process_map(OSMFILE, False)
   
    # # UNCOMMENT to see what tags are ignored
    # print "==========ignored tags==========="
    # print weird_set

    # pprint.pprint(data)
    

if __name__ == "__main__":
    test()