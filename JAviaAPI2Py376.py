#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 30 10:50:05 2020
@author: roncavallo
See README for usage instructions
"""
import requests
import json
import time
import csv
from urllib.parse import urlparse

#import subfiles
import workitemparser
import timeboxes
import creds
import cfg

# This collects instance details like the url and the endpoint you want to target
def CollectApiInfo():
    cfg.apiendpoint = input("Enter the api endpoint for your instance in following format EG. ""cities"". It is very important that you spell this endpoint correctly. Please refer to the api documents E.G https://cprime.agilecraft.com/api-docs/public/ for the apiendpoints available : ")
    #print(apiendpoint)
    cfg.instanceurl = input("Enter the url for your instance in following format EG. ""https://cprime.agilecraft.com"" : ")
    ChkInput = input("Is this your correct instance and endpoint you want to work with?  " + cfg.instanceurl + " : " + cfg.apiendpoint + "  " + "\n")
    if (ChkInput == "N") or (ChkInput == "n"):
        CollectApiInfo()
    cfg.instanceurl = cfg.instanceurl + "/rest/align/api/2" ##### Mess with these couple of lines, and break all of the other defs! 
    cfg.apiendpoint = "/" + cfg.apiendpoint.lower()
    cfg.api1instance = urlparse(cfg.instanceurl)
    cfg.api1instance = cfg.api1instance.scheme + "://" + cfg.api1instance.netloc
    cfg.api1instance = cfg.api1instance + "/api"
    return cfg.instanceurl, cfg.apiendpoint, cfg.api1instance


#Collect some basic stuff from the instance that provide information needed for adding work items
def CollectBasicItems():
    print ("Please wait about between 30 - 60 seconds while we collect some information from the Jira Align instance. Don't quit before the magic happens......")
# # GET REGIONS
    global regArr
    regArr = []
    regions = requests.get(cfg.instanceurl + "/regions", auth=cfg.BearerAuth(creds.jatoken))
    dataReg = regions.json()
    for eachReg in dataReg:
        #print(eachReg)
        region = eachReg['name']
        regionid = eachReg['id']
        regArr.append("Region Name: " + region + " " + " / Region ID: " + str(regionid))
 
# #GET CITIES
    global citArr
    citArr = []
    cities= requests.get(cfg.instanceurl + "/cities",  auth=cfg.BearerAuth(creds.jatoken))
    dataCit = cities.json()
    for eachCit in dataCit:
        cityID = eachCit['id']
        cityN = eachCit['name']
        cityRegionId = eachCit['regionId']

        citArr.append("City Name: " + cityN + " / City ID: " + str(cityID) + " / City Region ID: " + str(cityRegionId) + " / LastUpdatedDate: ")

    
# V1 GET ENTERPRISE HIERARCHY   
    global orgArr
    orgArr = []
    enterpriseH = requests.get(cfg.api1instance + "/organizationstructures",  auth=(creds.username, creds.jatoken))
    entData = enterpriseH.json()
    for eachOrg in entData['Results']:
            orgID = eachOrg['OrganizationStructureID']
            orgName = eachOrg['OrganizationStructureName']
            orgArr.append("Organization Name: " + orgName + " " + " / Organization ID: " + str(orgID))
        
# V1 GET COST CENTERS
    global costArr
    costArr = []
    CostCenters = requests.get(cfg.api1instance + "/costcenters",  auth=(creds.username, creds.jatoken))
    costData = CostCenters.json()
    for costCen in costData['Results']:
        costCentID = costCen['ID']
        costCentName = costCen['Name']
        costArr.append("Costcenter Name: " + costCentName + " " + " / Costcenter ID: " + str(costCentID))
   
    return regArr, citArr, orgArr, costArr     

#V2 GET Capabilities
def Capability():
    global capArr
    capArr = []
    Capabilities = requests.get(instanceurl + "/capabilities", auth=BearerAuth(jatoken))
    capData = Capabilities.json()   
    for eachCap in capData:
        #print(eachCap['title'])
        capID = eachCap['id']
        capTitle = eachCap['title']
        #capArr.append(("Capability ID: " + str(capID) + " " + " / Capability Name: " + capTitle))
        capArr.append(str(capID)+","+capTitle)
    return capArr
        
#V2 GET Users
def User():    
    global usrArr
    usrArr = []
    users = requests.get(instanceurl + "/users",  auth=BearerAuth(jatoken))
    data = users.json()
    for eachUsr in data:
        fn = eachUsr["firstName"]
        ln = eachUsr["lastName"]
        un = eachUsr['uid']
        em = eachUsr['email']
        usrArr.append(fn + ',' + ln + "," + un + ',' + em)
    return usrArr

#V2 GET Programs
def Program():
    global progArr
    progArr = []
    programs = requests.get(cfg.instanceurl + "/programs", auth=cfg.BearerAuth(creds.jatoken))
    progData = programs.json()
    for eachProg in progData:
        progName = eachProg['title']
        progID = eachProg['id']
        progArr.append(progName + "," + str(progID))
    return progArr

#V2 GET Product List for when Products are mandatory on Feature creations
def Product():
    global prodArr
    prodArr = []
    products = requests.get(cfg.instanceurl + "/products", auth=cfg.BearerAuth(creds.jatoken))
    prodData = products.json()
    for eachProd in prodData:
        prodName = eachProd['title']
        prodID = eachProd['id']
        prodArr.append(prodName + "," + str(prodID))
        #print (prodName,prodID)
    return prodArr

                
            
# This function is for collecting unique user-specific information for creating users such as email address etc. 
            
def CollectUserInfo():
    global UsrEmail
    UsrEmail = input("Please enter the full email address of the user [eg: ron.cavallo@cprime.com]")
    if not UsrEmail:
        UsrEmail = input("You must enter the full email address of the user [eg: ron.cavallo@cprime.com]")##This needs better checking 
    global UsrFN
    UsrFN = input("Please enter the full first name of the new user [eg: Jimeny]")
    if not UsrFN:
        UsrFN = input("You must enter the first name the user [eg: Jimeny]")
    global UsrLN
    UsrLN = input("Please enter the last name of the new user [eg: Cricket]")
    if not UsrLN:
        UsrFN = input("You must enter the last name the user [eg: Cricket]")
    return UsrEmail,UsrFN,UsrLN
    
        
#These functions create objects as per their name using POST commands 

def CreateUser(UsrE, UsrF, UsrL):
    UsrData = { "email" : UsrE, "FirstName" : UsrF, "LastName" : UsrL, "RoleID": "6", "Title": "CRM+ User", "EnterpirseHierarchy" : "16", "RegionID" : "1","CityID" : "14","CostCenterID" : "1" }
    #header = {"content-type": "application/json"}
    header = {"content-type": "appilcation/json", "Accept": "text/plain"}
    NewUser = requests.post(url = instanceurl+apiendpoint,data=json.dumps(UsrData), headers=header, verify=False, auth=(username, jatoken))

# This function creates a city with a post. Contrary to API documentation, these are the only two fields required to create a field
def CreateCity(newName, existingRegionID):
    paramData = {"Name" : newName, "RegionID" : existingRegionID}
    header = {"Content-Type": "application/json"}
    newCityPost = requests.post(url = instanceurl+apiendpoint, data=json.dumps(paramData), headers=header, verify=True, auth=(username, jatoken))
    print (newCityPost.status_code)

# This function creates an organization with a post. You only need to specify the name of the new org the ID will be automatically generated
def CreateOrg(newName):
    paramData = {"Name" : newName}
    header = {"Content-Type": "application/json"}
    newOrgPost = requests.post(url = instanceurl+apiendpoint, data=json.dumps(paramData), headers=header, verify=True, auth=(username, jatoken))
    print (newOrgPost.status_code)

def CreateCap(titl,desc,progID,parenID):
    #print(progID,parenID)
    paramData = {"title" : titl,"description" : desc, "programid" : progID, "state" : "1", "type" : "1", "parentId" : parenID}
    header = {"Content-Type": "application/json"}
    newCapPost = requests.post(url = instanceurl+apiendpoint, data=json.dumps(paramData), headers=header, verify=True, auth=BearerAuth(jatoken))
    print (newCapPost.status_code, newCapPost.text)

def CreateFeat(titl,desc,progID,parenID,prodID):
    print(titl,desc,progID,parenID)
    paramData = {"title" : titl,"description" : desc, "programid" : progID, "state" : "0", "type" : "1", "parentId" : parenID, "productId" : prodID}
    header = {"Content-Type": "application/json"}
    newFeatPost = requests.post(url = cfg.instanceurl+cfg.apiendpoint, data=json.dumps(paramData), headers=header, verify=True, auth=cfg.BearerAuth(creds.jatoken))
    #newFeatPost = requests.post(url = cfg.instanceurl+cfg.apiendpoint, data=json.dumps(paramData), headers=header, verify=True, auth=cfg.BearerAuth(creds.jatoken))
    print("Status Code - looking for 201's: " + str(newFeatPost.status_code))

#Handles the logic for EXPORT and IMPORT and parses several arrays to give the user choices over parameters during import
def CapRoutine(): 
    addCap = input("Do you want to import new Capabilities in your instance? If 'No' we will just output a list of the existing Capabilities to a csv file called caplist.csv in the directory this script is located [Y/N]:"+'\n')
    if (addCap== "Y") or (addCap == "y"):
        capInpt = input("Please place the csv file containing the capabilities you want to import, which is properly formatted in the directory with this script that contains the capabilities you want to import [Type ""OK""]" + '\n')
        capInpt = input("Type the name of the input csv file exactly here with .csv extension included:" + "\n")
        ChkInput = input("Is this the correct file name with .csv extension included? " + capInpt + " Type [Y/N]" + "\n")
        # Lets check if they are happy with their input, and if not start again and they can input the correct information
        if (ChkInput == "N") or (ChkInput == "n"):
            CapRoutine()
        time.sleep(5)
        #Fire off the Capability function to collect all of the capabilities
        Capability()
        #Loop through the possible programs you are going to assign as primary program for these capabiltiee
        for each in progArr:
            print (each)
        capProgID = input("From the list above, type the ID NUMBER of the Primary Program you assign to these imported capabilties. You MUST choose a primary Program for them. You may need to import in batches to get all of your Capabilities into the right Programs" + "\n")
        capParID = input("Type the ID number of the Parent Portfolio Epic (Not the name! - get ID from your JIRAALIGN List of PORTFOLIO EPICS) or EQUIVALENT work item in this instance" + "\n")
        ChkInput = input("Is this the correct Primary Program and correct Parent Program Epic to assign these capabilties? " + capProgID + " " + capParID + " Type [Y/N]" + "\n")
        if (ChkInput == "N") or (ChkInput == "n"):
            CapRoutine()
        with open(capInpt) as cap_inpt_file:
            csv_reader = csv.DictReader(cap_inpt_file)
            line_count = 0  
            for row in csv_reader:
                capTitle = row['title']
                description = row['description']
                state = row['state']
                typ = row['type']
                CreateCap(capTitle,capProgID, capParID)
                line_count += 1
            print(f'Processed {line_count} lines.')
    else:
        with open('caplist.csv', 'w', newline = '') as myfile:
            print ("This script is now going to create a comma delimited file called caplist.csv in the same directory of this script with all of the users listed \n")
            out = csv.writer(myfile,delimiter=',',quoting=csv.QUOTE_NONE, escapechar=' ')
            out.writerow(["title","description","id","parentID","programID","inRecycleBin"])
            for eachCap in workitemparser.itemArr:
                    #print(eachFeat)
                    out.writerow([eachCap]) #write each out to csv

#Handles the logic for EXPORT and IMPORT and parses several arrays to give the user choices over parameters during import
def FeatRoutine():
    addFeat = input("You have a choice of either IMPORTING or EXPORTING Features from here." + "\n" + "Type I for import or E for export [I or E]:"+'\n')
    if (addFeat== "I") or (addFeat == "i"):
        featInpt = input("Please place the csv file containing the FEATURES you want to import, which is properly formatted in the directory with this script that contains the FEATURES you want to import [Type ""OK""]" + '\n')
        featInpt = input("Type the name of the input csv file exactly here with .csv extension included:" + "\n")
        ChkInput = input("Is this the correct file name with .csv extension included? " + featInpt + " Type [Y/N]" + "\n")
        # Lets check if they are happy with their input, and if not start again and they can input the correct information
        if (ChkInput == "N") or (ChkInput == "n"):
            FeatRoutine()
        time.sleep(5)
        #Loop through the possible programs collected in CollectBasic function you are adding as Primary Program to imported Features
        for each in progArr:
            print (each)
        featProgID = input("From the list above, type the ID NUMBER of the Primary Program you assign to these imported Features. You MUST choose a primary program for them. You may need to import in batches to get all of your features into the right Programs" + "\n")
        #Loop through the possible programs collected in CollectBasic function you are adding as Primary Program to imported Features
        for each in prodArr:
            print (each)
        featProdID = input("From the list above, type the ID NUMBER of the PRODUCT you assign to these imported Features. You MUST choose a Product for them, you can always change it later. '\n' You may need to import in batches to get all of your features with the correct Products if they have to go to the correct Product on the initial import" + "\n")
        # Assign thw Feature a Parent.
        featParID = input("Type the ID number of the Capability OR EQUIVALENT (Not the name! - get ID from your JIRAALIGN List of CAPABILITIES) or EQUIVALENT work item in this instance" + "\n")
        ChkInput = input("Is this the correct Primary Program ,Capability, and Product to assign these Features to? " + featProgID + " " + featParID + " " + featProdID + " Type [Y/N]" + "\n")
        if (ChkInput == "N") or (ChkInput == "n"):
            FeatRoutine()
        with open(featInpt) as feat_inpt_file:
            csv_reader = csv.DictReader(feat_inpt_file)
            for row in csv_reader:
                featTitle = row['title']
                featDesc = row['description']
                # Hand off to def for creating Features
                CreateFeat(featTitle,featDesc,featProgID,featParID,featProdID)
    else:
        print ("This script has exported the list of Features from: " + cfg.instanceurl + " to a file called featlist.csv in the same directory of this script" + " \n")
        with open('featlist.csv', 'w', newline = '') as myfile:
            out = csv.writer(myfile,delimiter=',',quoting=csv.QUOTE_NONE, escapechar=' ')
            out.writerow(["title","description","id","parentID","programID","inRecycleBin"])
            for eachFeat in workitemparser.itemArr:
                #print(eachFeat)
                out.writerow([eachFeat]) #write each out to csv

def EpicRoutine():
    addEpic = input("You have a choice of either IMPORTING or EXPORTING Portfolio Epics from here." + "\n" + "Type I for import or E for export [I or E]:"+'\n')
    if (addEpic== "I") or (addEpic == "i"):
        EpicInpt = input("Please place the csv file containing the FEATURES you want to import, which is properly formatted in the directory with this script that contains the FEATURES you want to import [Type ""OK""]" + '\n')
        epicInpt = input("Type the name of the input csv file exactly here with .csv extension included:" + "\n")
        ChkInput = input("Is this the correct file name with .csv extension included? " + epicInpt + " Type [Y/N]" + "\n")
        # Lets check if they are happy with their input, and if not start again and they can input the correct information
        if (ChkInput == "N") or (ChkInput == "n"):
            EpicRoutine()
        time.sleep(5)
        #Loop through the possible programs collected in CollectBasic function you are adding as Primary Program to imported epic
        for each in progArr:
            print (each)
        epicProgID = input("From the list above, type the ID NUMBER of the Primary Program you assign to these imported epic. You MUST choose a primary program for them. You may need to import in batches to get all of your epic into the right Programs" + "\n")
        #Loop through the possible programs collected in CollectBasic function you are adding as Primary Program to imported epic
        for each in prodArr:
            print (each)
        epicProdID = input("From the list above, type the ID NUMBER of the PRODUCT you assign to these imported epic. You MUST choose a Product for them, you can always change it later. '\n' You may need to import in batches to get all of your epic with the correct Products if they have to go to the correct Product on the initial import" + "\n")
        # Assign thw epicure a Parent.
        epicParID = input("Type the ID number of the Capability OR EQUIVALENT (Not the name! - get ID from your JIRAALIGN List of CAPABILITIES) or EQUIVALENT work item in this instance" + "\n")
        ChkInput = input("Is this the correct Primary Program ,Capability, and Product to assign these epic to? " + epicProgID + " " + epicParID + " " + epicProdID + " Type [Y/N]" + "\n")
        if (ChkInput == "N") or (ChkInput == "n"):
            epicRoutine()
        with open(epicInpt) as epic_inpt_file:
            csv_reader = csv.DictReader(epic_inpt_file)
            for row in csv_reader:
                epicTitle = row['title']
                epicDesc = row['description']
                # Hand off to def for creating epic
                CreatEpic(epicTitle,epicDesc,epicProgID,epicParID,epicProdID)
    else:
        print ("This script has exported the list of Portfolio Epics from: " + cfg.instanceurl + " to a file called epiclist.csv in the same directory of this script" + " \n")
        with open('epiclist.csv', 'w', newline = '',encoding='utf-8') as myfile:
            #out = csv.writer(myfile,delimiter=',',quoting=csv.QUOTE_NONE, escapechar=' ')
            out = csv.writer(myfile,delimiter=',',quoting=csv.QUOTE_NONE, escapechar=' ')
            out.writerow(["title","description","id","parentID","programID","inRecycleBin"])
            for eachepic in workitemparser.itemArr:
                #print(eachepic)
                out.writerow([eachepic]) #write each out to csv

def ThemeRoutine():
    addtheme = input("You have a choice of either IMPORTING or EXPORTING Portfolio themes from here." + "\n" + "Type I for import or E for export [I or E]:"+'\n')
    if (addtheme== "I") or (addtheme == "i"):
        themeInpt = input("Please place the csv file containing the FEATURES you want to import, which is properly formatted in the directory with this script that contains the FEATURES you want to import [Type ""OK""]" + '\n')
        themeInpt = input("Type the name of the input csv file exactly here with .csv extension included:" + "\n")
        ChkInput = input("Is this the correct file name with .csv extension included? " + themeInpt + " Type [Y/N]" + "\n")
        # Lets check if they are happy with their input, and if not start again and they can input the correct information
        if (ChkInput == "N") or (ChkInput == "n"):
            themeRoutine()
        time.sleep(5)
        #Loop through the possible programs collected in CollectBasic function you are adding as Primary Program to imported theme
        for each in progArr:
            print (each)
        themeProgID = input("From the list above, type the ID NUMBER of the Primary Program you assign to these imported theme. You MUST choose a primary program for them. You may need to import in batches to get all of your theme into the right Programs" + "\n")
        #Loop through the possible programs collected in CollectBasic function you are adding as Primary Program to imported theme
        for each in prodArr:
            print (each)
        themeProdID = input("From the list above, type the ID NUMBER of the PRODUCT you assign to these imported theme. You MUST choose a Product for them, you can always change it later. '\n' You may need to import in batches to get all of your theme with the correct Products if they have to go to the correct Product on the initial import" + "\n")
        # Assign thw themeure a Parent.
        themeParID = input("Type the ID number of the Capability OR EQUIVALENT (Not the name! - get ID from your JIRAALIGN List of CAPABILITIES) or EQUIVALENT work item in this instance" + "\n")
        ChkInput = input("Is this the correct Primary Program ,Capability, and Product to assign these theme to? " + themeProgID + " " + themeParID + " " + themeProdID + " Type [Y/N]" + "\n")
        if (ChkInput == "N") or (ChkInput == "n"):
            ThemeRoutine()
        with open(themeInpt) as theme_inpt_file:
            csv_reader = csv.DictReader(theme_inpt_file)
            for row in csv_reader:
                themeTitle = row['title']
                themeDesc = row['description']
                # Hand off to def for creating theme
                Creattheme(themeTitle,themeDesc,themeProgID,themeParID,themeProdID)
    else:
        print ("This script has exported the list of Portfolio themes from: " + cfg.instanceurl + " to a file called themelist.csv in the same directory of this script" + " \n")
        with open('themelist.csv', 'w', newline = '',encoding='utf-8') as myfile:
            #out = csv.writer(myfile,delimiter=',',quoting=csv.QUOTE_NONE, escapechar=' ')
            out = csv.writer(myfile,delimiter=',',quoting=csv.QUOTE_NONE, escapechar=' ')
            out.writerow(["title","description","id","parentID","programID","inRecycleBin"])
            for eachtheme in workitemparser.itemArr:
                #print(eachtheme)
                out.writerow([eachtheme]) #write each out to csv
    
def CitHandler():
    addCity = input("Do you want to create a new City in your Jira Align instance? [Y/N]:"+'\n')
    if (addCity == "Y") or (addCity == "y"):
        print ("You must specify a NEW CITY NAME, and an EXISTING REGION ID NUMBER in order to add a new City. Here is a list of all Cities with City ID's and Regions with Region ID's in Jira Align from your instance \n")
        for cit in citArr:
            print (cit)
        for reg in regArr:
            print (reg)
        existRegionID = input("Please enter the ID NUMBER of the EXISTING Region you would like to add your new City to [eg: US]")
        existRegionID = int(existRegionID)
        newCityName = input("Please enter the name of the new City you would like to create [eg: Atlanta]")
        CreateCity(newCityName,existRegionID)
    else:
        print ("Here is a list of all cities and thier IDs in Jira Align from your instance \n")
        for cit in citArr:
            print (cit)


#def IterationRoutine():
    


####################################################################################################################################################################################
def main():
####################################################################################################################################################################################
# MAIN
  
    # Call a subfile that helps handle shared routines and variables between this file and other files like workitemparser, jathemes, etc
    cfg.init()
    
    #Collect api server and endpoint. Also collect all of the instance json infomation we need into arrays with CollectUsrMenuItems
    CollectApiInfo()
    #print(instanceurl+apiendpoint)
 
    #Dat collects information you will need later if you want to create users at all, and in some cases work items.
    CollectBasicItems()

    #Features
    if "features" in cfg.apiendpoint:     
        Product()
        # Call Feature from the workitemparser file so that you can build the complete list of Features into an array
        workitemparser.FeatsOrCaps("features")
        # Call the FeatRoutine that utilizes the array that is created in Features and puts them into a csv file.
        Program()
        FeatRoutine()
    
    #Capabilities
    if "capabilities" in cfg.apiendpoint:
        workitemparser.FeatsOrCaps("capabilities")
        Program()
        CapRoutine()
  
    #Portfolio Epics
    if "epics" in cfg.apiendpoint:
        workitemparser.FeatsOrCaps("epics")
        Program()
        EpicRoutine()   

    # Themes
    if "themes" in cfg.apiendpoint:
        workitemparser.FeatsOrCaps("themes")
        Program()
        ThemeRoutine()
        
    if "iterations" in cfg.apiendpoint:
        timeboxes.grabit("iterations")

####################################################################################################################################################################################       
if __name__ == "__main__":
    main()     
####################################################################################################################################################################################

