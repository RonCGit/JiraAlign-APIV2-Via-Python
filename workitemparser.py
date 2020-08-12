# -*- coding: utf-8 -*-
"""
Created on Mon Jul 13 14:19:13 2020

@author: ron.cavallo@cprime.com

This file handles parsing the features in the entire instance. There is code here that works around the api limit of 100 records
by paginating and using the "skip" argument in the API

"""
import requests
#import the shared file with shared defs, classes, and variables
import cfg
# import the credentials file. NEVER ADD TO REPO!
import creds

# This ugly beast parses through all of the work items and puts the values we want from the work items into an array with a comma between the values.
def FeatsOrCaps(which):
    global itemArr
    itemArr = []
    featorcap = requests.get(cfg.instanceurl + "/" + which, auth=cfg.BearerAuth(creds.jatoken))
    Data = featorcap.json()
    line_count = 0
    # Starting point for skipping is to go to the next 100..
    skip = 100
    for eachWorkItem in Data:
        line_count += 1
        itemName = eachWorkItem['title']
        # Replace all commas to preserve comma delimited format that the csv.writer module is using with dashes
        itemName = cfg.ReplaceStrings(itemName,",","-")
        itemName = cfg.RemoveEOLChar(itemName)
        itemDesc = eachWorkItem['description']
        # Replace all commas to preserve comma delimited format that the csv.writer module is using with dashes
        itemDesc = cfg.ReplaceStrings(itemDesc,",","-")
        # Remove line feeds and carriage returns from description
        itemDesc = cfg.RemoveEOLChar(itemDesc)
        if not itemDesc:
            itemDesc = ''
        itemID = eachWorkItem['id']
        # The name of the key that represents the parent item is differnt for Epic than it is for features and capabilities, so handle that. 
        # We also make sure that if it is "none" then we set it to a blank space instead since handling nones is a pita
        if which == "epics":
            itemParent = eachWorkItem['themeId']
        else:
            itemParent = eachWorkItem['parentId']
        if not itemParent:
            itemParent = ''
        itemProg = eachWorkItem['programId']
        itemIsDel = eachWorkItem['inRecycleBin']
        # ONLY Take items that are not in the recycle bin
        # Epics have different values for the key inRecycleBin so handle that first. Its either null or 1. Duh.
        if itemIsDel is None:
            line_count += 1
            itemArr.append(itemName + "," + itemDesc + "," + str(itemID) + "," + str(itemParent) + "," + str(itemProg))
        # For Features and Capabilties, the values for that key are boolean. Duh again.
        if itemIsDel == False:
            line_count += 1
            itemArr.append(itemName + "," + itemDesc + "," + str(itemID) + "," + str(itemParent) + "," + str(itemProg))
        #If it turns out this is a deleted item, finally, do not add it to array and skip it
        else:
            continue
    if len(Data) < 100:
        return itemArr
    if len(Data) == 100:
        moreItems = requests.get(cfg.instanceurl + "/" + which + "?&$skip=" + str(skip), auth=cfg.BearerAuth(creds.jatoken))
        moreData = moreItems.json()
        skip += 100
        for anotherItem in moreData:
            moitemName = anotherItem['title']      
            # Replace all commas to preserve comma delimited format that the csv.writer module is using with dashes
            moitemName = cfg.ReplaceStrings(moitemName,",","-")
            # Remove any line feeds or carriage returns that snuck into the title
            moitemName = cfg.RemoveEOLChar(moitemName)
            moitemDesc = anotherItem['description']
            # Replace all commas to preserve comma delimited format that the csv.writer module is using with dashes
            moitemDesc = cfg.ReplaceStrings(moitemDesc,",","-")
            # Remove any line feeds or carriage returns in the description
            moitemDesc = cfg.RemoveEOLChar(moitemDesc)
            if not moitemDesc:
                moitemDesc = ''
            moitemID = anotherItem['id']
            # The name of the key that represents the parent item is differnt for Epic than it is for features and capabilities, so handle that. 
            # We also make sure that if it is "none" then we set it to a blank space instead since handling nones is a pita
            if which == "epics":
                moitemParent = anotherItem['themeId']
            else:
                moitemParent = anotherItem['parentId']
            if not moitemParent:
                moitemParent = ''
            moitemProg = anotherItem['programId']
            mofeatIsDel = anotherItem['inRecycleBin']
            # ONLY Take items that are not in the recycle bin
            # Epics have different values for the key inRecycleBin so handle that first. Its either null or 1. Duh.
            if mofeatIsDel is None:
                line_count += 1
                itemArr.append(moitemName + "," + moitemDesc + "," + str(moitemID) + "," + str(moitemParent) + "," + str(moitemProg))
            # For Features and Capabilties, the values for that key are boolean. Duh again.
            if mofeatIsDel == False:
                # Increment lines processed, then only put the key - values that we want into the array, with a comma inserted in between each value
                line_count += 1
                itemArr.append(moitemName + "," + moitemDesc + "," + str(moitemID) + "," + str(moitemParent) + "," + str(moitemProg))
            else:
                continue
        while len(moreData) > 1:
            manyItems = requests.get(cfg.instanceurl + "/" + which + "?&$skip=" + str(skip), auth=cfg.BearerAuth(creds.jatoken))
            manyitemData = manyItems.json()
            skip += 100
            print(skip)
            for manyItem in manyitemData:
                manyitemName = manyItem['title']
                #Clean up the names when they have a carriage or line feed in it.
                manyitemName = cfg.RemoveEOLChar(manyitemName)
                # Replace all commas in the name to preserve comma delimited format that the csv.writer module is using with dashes
                manyitemName = cfg.ReplaceStrings(manyitemName,",","-")
                manyitemDesc = manyItem['description']
                #print(manyitemDesc)
                # Replace all commas to preserve comma delimited format that the csv.writer module is using with dashes
                manyitemDesc = cfg.ReplaceStrings(manyitemDesc,",","-")
                # Remove BOTH Line Feeds and Carriage returns from the Description field there are usually tons.
                manyitemDesc = cfg.RemoveEOLChar(manyitemDesc)
                if not manyitemDesc:
                    manyitemDesc = ''
                manyitemID = manyItem['id']
                # The name of the key that represents the parent item is differnt for Epic than it is for features and capabilities, so handle that. 
                # We also make sure that if it is "none" then we set it to a blank space instead since handling nones is a pita
                if which == "epics":
                    manyitemParent = manyItem['themeId']
                else:
                    manyitemParent = manyItem['parentId']
                # If there is no parent specified remove the word "None" from the return json
                if not manyitemParent:
                      manyitemParent = ''
                manyitemProg = manyItem['programId']
                manyitemIsDel = manyItem['inRecycleBin']
                # ONLY Take items that are NOT in the recycle bin
                # Epics have different values for the key inRecycleBin so handle that first. Its either null or 1. Duh.
                if manyitemIsDel is None:
                    line_count += 1
                    itemArr.append((manyitemName if manyitemName else "") +"," + (manyitemDesc if manyitemDesc else "")+","+ (str(manyitemID) if manyitemID else "") +"," + (str(manyitemParent) if manyitemParent else "") + ","+(str(manyitemProg) if manyitemProg else ""))
                # For Features and Capabilties, the values for that key are boolean. Duh again.
                if manyitemIsDel == False:
                    line_count += 1
                    itemArr.append((manyitemName if manyitemName else "") +"," + (manyitemDesc if manyitemDesc else "")+","+ (str(manyitemID) if manyitemID else "") +"," + (str(manyitemParent) if manyitemParent else "") + ","+(str(manyitemProg) if manyitemProg else ""))
                else:
                     continue
            if len(manyItems.json()) < 99:        
                lastItems = requests.get(cfg.instanceurl + "/" + which + "?&$skip=" + str(skip), auth=cfg.BearerAuth(creds.jatoken))
                lastitemData = lastItems.json()
                for lastItem in lastitemData:
                    lastitemName = lastItem['title']
                    #Clean up the names when they have a carriage or line feed in it.
                    lastitemName = cfg.RemoveEOLChar(lastitemName)
                    # Replace all commas in the name to preserve comma delimited format that the csv.writer module is using with dashes
                    lastitemName = cfg.ReplaceStrings(lastitemName,",","-")
                    lastitemDesc = lastItem['description']
                    #print(lastitemDesc)
                    # Replace all commas to preserve comma delimited format that the csv.writer module is using with dashes
                    lastitemDesc = cfg.ReplaceStrings(lastitemDesc,",","-")
                    # Remove BOTH Line Feeds and Carriage returns from the Description field there are usually tons.
                    lastitemDesc = cfg.RemoveEOLChar(lastitemDesc)
                    if not lastitemDesc:
                        lastitemDesc = ''
                    lastitemID = lastItem['id']
                    # The name of the key that represents the parent item is differnt for Epic than it is for features and capabilities, so handle that. 
                    # We also make sure that if it is "none" then we set it to a blank space instead since handling nones is a pita
                    if which == "epics":
                        lastitemParent = lastItem['themeId']
                    else:
                        lastitemParent = lastItem['parentId']
                    # If there is no parent specified remove the word "None" from the return json
                    if not lastitemParent:
                          lastitemParent = ''
                    lastitemProg = lastItem['programId']
                    lastitemIsDel = lastItem['inRecycleBin']
                    # ONLY Take items that are NOT in the recycle bin
                    if lastitemIsDel is None:
                        line_count += 1
                        itemArr.append((lastitemName if lastitemName else "") +"," + (lastitemDesc if lastitemDesc else "")+","+ (str(lastitemID) if lastitemID else "") +"," + (str(lastitemParent) if lastitemParent else "") + ","+(str(lastitemProg) if lastitemProg else ""))
                    if lastitemIsDel == False:
                        # Increment lines processed, then only put the key - values that we want into the array, with a comma inserted in between each value
                        line_count += 1
                        itemArr.append((lastitemName if lastitemName else "") +"," + (lastitemDesc if lastitemDesc else "")+","+ (str(lastitemID) if lastitemID else "") +"," + (str(lastitemParent) if lastitemParent else "") + ","+(str(lastitemProg) if lastitemProg else ""))
                    else:
                        continue
                break
    print (len(itemArr))
    print('Processed ' + str(line_count) + " " + which)
    return itemArr


