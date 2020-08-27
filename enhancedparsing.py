# -*- coding: utf-8 -*-
"""
Created on Fri Aug 14 13:28:11 2020

@author: cpadmin
"""
import requests
import cfg
import creds
import json

##################
def jajsonparser(which,key1,key2,key3,key4,key5,key6):
##################
    global arrname
    arrname = which+'Arr'
    arrname = []
    name = which+'Name'
    iters = requests.get(cfg.instanceurl + "/" + which, auth=cfg.BearerAuth(creds.jatoken))
    data = iters.json()
    line_count = 0
    #print(json.dumps(data))
    for iter in data:
        title = (iter[key1])
        startdate = str(iter[key2])
        enddate = str(iter[key3])
        anchorSprintID = str(iter[key4])
        progID = str(iter[key5])
        print(title, startdate, enddate, anchorSprintID,progID)