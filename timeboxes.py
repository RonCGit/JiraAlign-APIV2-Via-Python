# -*- coding: utf-8 -*-
"""
Created on Fri Aug 14 13:28:11 2020

@author: cpadmin
"""
import requests
import cfg
import creds


def grabit(which):
    global arrname
    arrname = which+'Arr'
    arrname = []
    name = which+'Name'
    iters = requests.get(cfg.instanceurl + "/" + which, auth=cfg.BearerAuth(creds.jatoken))
    data = iters.json()
    line_count = 0
    for iter in data:
        print (iter)
        name = iter['title']
        # = str(item['id'])
        # item+'ReleaseId' = str(iter['releaseId'])
        print(name)
        