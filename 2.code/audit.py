#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Functions to audit and update the OSMFILE 

Example:
    $ python audit.py
    Output:
    Atlas Peak => Atlas Peak Drive
    Highway 7 => 7 Highway


"""
import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

OSMFILE = "../4.richmondhill_sample.osm"
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons", "Crescent", "Way", "Circle", "Sideroad", "Gardens", "Gate",
            "Chase", "Circuit", "Hollow", "Manor", "Meadow","Mews", "Park", "Path", "Ridge","Terrace",
            "Wood", "Gateway", "Grove", "Harbour" , "Highway", "Hill"]
mapping = { "Crt." : "Court",
            "By-pass" : "Avenue",
            "Rd" : "Road",
            "Dr" : "Drive",
            "Yonge" : "Yonge Street",
            "Peak" : "Peak Drive",
            "Maple" : "Maple Street"}
directions = ['East', 'North', 'West' , 'South']
direction_mapping = {"E" : "East",
                     "W" : "West",
                     "S" : "South",
                     "N" : "North"}


def audit_street_type(street_types, street_name):
    """Function to audit a street type
    Check if the street_name has street_type NOT in the expected list
    If not, add the street name and it's street type to the street_types 
    dictionary and returns the dictionary 
    
    Args: 
        street_types (defaultdict(set)): dictionary of already audited street_types
        street_name (str): street_name to be audited 

    Returns: 
        street_types (defaultdict(set)): dictionary after auditing street_name 

    """
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)
    return street_types


def is_street_name(elem):
    """function to check if an xml Element represents a street name

    Args:
        elem (Element): The element to be checked

    Returns:
        bool: returns True if elem represents a street, False otherwise
    """
    return (elem.attrib['k'] == "addr:street")

def is_post_code(elem):
    """function to check if an xml Element represents a postal code

    Args:
        elem (Element): The element to be checked

    Returns:
        bool: returns True if elem represents a postal code, False otherwise
    """
    return (elem.attrib['k'] == "addr:postcode")

def audit(osmfile):
    """audit the street types in osmfile

    Args:
        osmfile (str): The location of the osmfile 

    Returns:
        street_types (defaultdict(set)): 
            keys: street_types(str) extract from street_names in osmfile 
                  NOT in 'expected' list of street_types
            values: set of all unique street_names in osmfile 
    """
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    street_types = audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()
    return street_types


def update_name(name, mapping=mapping, direction_mapping=direction_mapping, directions=directions):
    """Function to update the given street name 

    Args:
        name (str): Name to be updated
        mapping ({}): { bad_part (str) : corrected_part (str) }
        direction_mapping ({}): mapping for parts that represent directions
        directions ([]): list of directions 

    Returns:
        str : updated name 
    """
    name = update_special_names(name)
    # regular cases with street name at the end 
    m = street_type_re.search(name)
    if m:
        street_type = m.group()
        direction = None
        real_street_type = None
        # abbreviated street direction 
        if street_type in direction_mapping:
            street_type = direction_mapping[street_type]
        # streets with directions at the end
        if street_type in directions:
            direction = street_type
            name = name[:m.start()].strip()
            real_street_type = name.split(" ")[-1]
        # for streets w/t directions at the end 
        if not real_street_type:
            real_street_type = street_type
        # do the mapping of street types 
        if real_street_type in mapping:
            correct_street_type = mapping[real_street_type]
            name = name.replace(real_street_type, correct_street_type)
        # add back the direction to the names if available
        if direction:
            name +=  " "+direction
    return name

def update_postcode(postcode):
    """Function to update the given postcode

    Args:
        postcode (str): Postal code to be updated

    Returns:
        str : updated postcode, or None if postcode is not valid 

    Example:
        postcode = 'L1M2I4'
        print update_postcode(postcode)
        > L1M 2I4
    """
    if postcode.startswith("L"):
        m = re.findall(r'^(L\d[A-Z])\s?(\d[A-Z]\d)$', postcode)
        if m:
            groups = m[0]
            postcode = ' '.join(groups)
            return postcode
    else:
        return None 

def update_special_names(name):
    """Helper function of update_name
    This function is to deal with the special cases of street names in OSMFILE  

    Args:
        name (str): Name to be updated

    Returns:
        str : updated name 
    """
    if name == "Fox Point":
        return "FIXME"
    if name.startswith('Highway 7'):
        return '7 Highway'
    if name.endswith(', Ste 500'):
        return 'Allstate Parkway'
    if name.endswith(' #A3'):
        return 'Rutherford Rd' 
    return name

def test():
    st_types = audit(OSMFILE)
    #Uncomment to see the dictionary of uncommon street type : set (street names)
    pprint.pprint(dict(st_types))

    #Uncomment to update names 
    for st_type, ways in st_types.iteritems():
        for name in ways:
            better_name = update_name(name, mapping)
            print name, "=>", better_name
            
    #Uncomment to test the update_postcode function
    postcode = 'L1M2I4'
    print update_postcode(postcode)
if __name__ == '__main__':
    test()