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
from creds import *
import csv
from urllib.parse import urlparse



instanceurl = "None"
apiendpoint = "None"
#_______________________________________________________________________________

class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token
    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r
#_______________________________________________________________________________

# This collects all of the information about the server instance and api endpoint you want to work with and formats the url properly.
# This is the only place that the apiendpoint or the url should be manipulated or it breaks the rest of the routines that depend upon it.
def CollectApiInfo():
    global apiendpoint
    global instanceurl
    global api1instance
    apiendpoint = input("Enter the api endpoint for your instance in following format EG. ""cities"". It is very important that you spell this endpoint correctly. Please refer to the api documents E.G https://cprime.agilecraft.com/api-docs/public/ for the apiendpoints available : ")
    #print(apiendpoint)
    instanceurl = input("Enter the url for your instance in following format EG. ""https://cprime.agilecraft.com"" : ")
    ChkInput = input("Is this your correct instance and endpoint you want to work with?  " + instanceurl + " : " + apiendpoint + "  " + "\n")
    if (ChkInput == "N") or (ChkInput == "n"):
       CollectApiInfo()
    instanceurl = instanceurl + "/rest/align/api/2" ##### Mess with these couple of lines, and break all of the other defs! 
    apiendpoint = "/" + apiendpoint.lower()
    api1instance = urlparse(instanceurl)
    api1instance = api1instance.scheme + "://" + api1instance.netloc
    api1instance = api1instance + "/api"
    return instanceurl, apiendpoint, api1instance
        
#reuse this function to check if the user sees that they entered information correctly after reviewing it
def ChkInput(Input):
    while True:
        if (Input == 'N') or (Input == 'n'):
            return input
        else:
            break
#Since we are using csv files as the basis for import and export, we have to remove all of the commas from the text in the fields so commas are only field delimiters
def ReplaceStrings(txt,remove,replace):
    if txt and "," in txt:
        txt = txt.replace(remove,replace)
        return txt
    else:
        return txt

#Collect some basic stuff from the instance that provide information needed for adding work items
def CollectBasicItems():
    print ("Please wait about 30 seconds while we collect some information from the Jira Align instance. Do not end this process, just wait a bit...")
# # GET REGIONS
    global regArr
    regArr = []
    regions = requests.get(instanceurl + "/regions", auth=BearerAuth(jatoken))
    dataReg = regions.json()
    for eachReg in dataReg:
        #print(eachReg)
        region = eachReg['name']
        regionid = eachReg['id']
        regArr.append("Region Name: " + region + " " + " / Region ID: " + str(regionid))
 
# #GET CITIES
    global citArr
    citArr = []
    cities= requests.get(instanceurl + "/cities",  auth=BearerAuth(jatoken))
    dataCit = cities.json()
    for eachCit in dataCit:
        cityID = eachCit['id']
        cityN = eachCit['name']
        citArr.append("City Name: " + cityN + " " + " / City ID: " + str(cityID))

    
# V1 GET ENTERPRISE HIERARCHY   
    global orgArr
    orgArr = []
    enterpriseH = requests.get(api1instance + "/organizationstructures",  auth=(username, jatoken))
    entData = enterpriseH.json()
    for eachOrg in entData['Results']:
            orgID = eachOrg['OrganizationStructureID']
            orgName = eachOrg['OrganizationStructureName']
            orgArr.append("Organization Name: " + orgName + " " + " / Organization ID: " + str(orgID))
        
# V1 GET COST CENTERS
    global costArr
    costArr = []
    CostCenters = requests.get(api1instance + "/costcenters",  auth=(username, jatoken))
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
    programs = requests.get(instanceurl + "/programs", auth=BearerAuth(jatoken))
    progData = programs.json()
    for eachProg in progData:
        progName = eachProg['title']
        progID = eachProg['id']
        progArr.append(progName + "," + str(progID))
    return progArr

#This function formats arrays returned into a menu

def MenuChooser(message, arr):
    print (message+'\n')
    count = 0
    choice = ""
    listlen = len(arr)
    for number in range(0,listlen):
        count = count + 1
        print (str(count) + ":  ")
        print (arr[number] + " \n")
    choice = input("Please type the menu number preceeding the ':' of your choice  eg: 1 2 or 3 etc: \n")
    choice = int(choice) 
    choice = (choice - 1) # Since I start the menu with the number 1, but the element number in the array starts at 0, make them match
    for menuitems in range(0, listlen):
        if menuitems is choice:
            print ("Choice made: " + arr[choice] + " \n")
                
            
# This fuction is for collecting unique user-specific information for creating users such as email address etc. 
            
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

def CreateCap(titl,progID,parenID):
    print(progID,parenID)
    paramData = {"title" : titl,"description" : "testcap1 test", "programid" : progID, "state" : "1", "type" : "1", "parentId" : parenID}
    header = {"Content-Type": "application/json"}
    newCapPost = requests.post(url = instanceurl+apiendpoint, data=json.dumps(paramData), headers=header, verify=True, auth=BearerAuth(jatoken))
    print (newCapPost.status_code, newCapPost.text)

# Works togther with createcap. This function only handles the logic around capturing the information needed to create capabilities. The function CreateCap handles actually creating those capabilities after the infomation is collected
def CapHandler(): 
    addCap = input("Do you want to import new Capabilities in your instance? If 'No' we will just output a list of the existing Capabilities to a csv file called caplist.csv in the directory this script is located [Y/N]:"+'\n')
    if (addCap== "Y") or (addCap == "y"):
        capInpt = input("Please place the csv file containing the capabilities you want to import, which is properly formatted in the directory with this script that contains the capabilities you want to import [Type ""OK""]" + '\n')
        capInpt = input("Type the name of the input csv file exactly here with .csv extension included:" + "\n")
        ChkInput = input("Is this the correct file name with .csv extension included? " + capInpt + " Type [Y/N]" + "\n")
        # Lets check if they are happy with their input, and if not start again and they can input the correct information
        if (ChkInput == "N") or (ChkInput == "n"):
            CapHandler()
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
            CapHandler()
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
        print ("This script is now going to create a comma delimited file called caplist.csv in the same directory of this script with all of the users listed \n")
        with open('caplist.csv', 'w', newline='') as myfile:
            out = csv.writer(myfile,dialect='excel',delimiter=',',quoting=csv.QUOTE_NONE,escapechar=' ')
            for eachCap in capArr:
                print(eachCap)
                out.writerow([eachCap]) 

def FeatRoutine():
    #Available in Version 2 only - handles the Features endpoint
    addFeat = input("Do you want to import new Features in your instance? If 'No' we will just output a list of the existing Features to a csv file called featurelist.csv in the directory this script is located [Y/N]:"+'\n')
    if (addFeat== "Y") or (addFeat == "y"):
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
        featParID = input("Type the ID number of the Capability OR EQUIVALENT (Not the name! - get ID from your JIRAALIGN List of CAPABILITIES) or EQUIVALENT work item in this instance" + "\n")
        ChkInput = input("Is this the correct Primary Program and correct Capability to assign these Features to? " + featProgID + " " + featParID + " Type [Y/N]" + "\n")
        if (ChkInput == "N") or (ChkInput == "n"):
            FeatHandler()
        with open(featInpt) as feat_inpt_file:
            csv_reader = csv.DictReader(feat_inpt_file)
            for row in csv_reader:
                featTitle = row['title']
                description = row['description']
                state = row['state']
                typ = row['type']
                CreateFeat(featTitle,featProgID, featParID)
    else:
        print ("This script is now going to create a comma delimited file called featlist.csv in the same directory of this script" + " \n")
        with open('featlist.csv', 'w', newline='') as myfile:
            line_count = 0
            out = csv.writer(myfile,dialect='excel',delimiter=',',quoting=csv.QUOTE_NONE,escapechar=' ')
            for eachFeat in featArr:
                print(eachFeat)
                out.writerow([eachFeat]) #write each out to csv

#V2 GET Features
def Feature():
    global featArr
    featArr = []
    features = requests.get(instanceurl + "/features", auth=BearerAuth(jatoken))
    featData = features.json()
    #print(len(features.json()))
    line_count = 0
    for eachFeature in featData:
        line_count += 1
        featName = eachFeature['title']
        # Replace all commas to preserve comma delimited format that the csv.writer module is using with dashes
        featName = ReplaceStrings(featName,",","-")
        featID = eachFeature['id']
        featDesc = eachFeature['description']
        # Replace all commas to preserve comma delimited format that the csv.writer module is using with dashes
        featDesc = ReplaceStrings(featDesc,",","-")
        featParent = eachFeature['parentId']
        featProg = eachFeature['programId']
        featIsDel = eachFeature['inRecycleBin']
        featArr.append(featName + "," + str(featID) + "," + featDesc + "," + str(featParent) + "," + str(featProg) + "," + str(featIsDel))
    #check to see if we hit 100 and if so start working in groups of 100
    if len(features.json()) == 100:
        #set this value since the api allows skipping by an integer assigned to argument skip
        skip = int(100)
        moreFeatures = requests.get(instanceurl + "/features?$select=id,title,description,programId,parentId,inRecycleBin&$skip=" + str(skip), auth=BearerAuth(jatoken))
        mofeatData = moreFeatures.json()
        #print(len(moreFeatures.json()))
        for anotherFeat in mofeatData:
            line_count += 1
            mofeatName = anotherFeat['title']      
            # Replace all commas to preserve comma delimited format that the csv.writer module is using with dashes
            mofeatName = ReplaceStrings(mofeatName,",","-")
            mofeatID = anotherFeat['id']
            mofeatDesc = anotherFeat['description']
            # Replace all commas to preserve comma delimited format that the csv.writer module is using with dashes
            mofeatDesc = ReplaceStrings(mofeatDesc,",","-")
            mofeatParent = anotherFeat['parentId']
            mofeatProg = anotherFeat['programId']
            mofeatIsDel = anotherFeat['inRecycleBin']
            featArr.append(mofeatName + "," + str(mofeatID) + "," + mofeatDesc + "," + str(mofeatParent) + "," + str(mofeatProg) + "," + str(mofeatIsDel))
    manyFeatures = requests.get(instanceurl + "/features?$select=id,title,description,programId,parentId,inRecycleBin&$skip=" + str(skip), auth=BearerAuth(jatoken))
    manyfeatData = manyFeatures.json()
    while len(manyFeatures.json()) > 1:
        manyFeatures = requests.get(instanceurl + "/features?$select=id,title,description,programId,parentId,inRecycleBin&$skip=" + str(skip), auth=BearerAuth(jatoken))
        manyfeatData = manyFeatures.json()
        #print(len(manyFeatures.json()))
        skip = int(skip+100)
        for addFeat in manyfeatData:
            line_count += 1
            manyfeatName = addFeat['title']      
            # Replace all commas to preserve comma delimited format that the csv.writer module is using with dashes
            manyfeatName = ReplaceStrings(manyfeatName,",","-")
            manyfeatID = addFeat['id']
            manyfeatDesc = addFeat['description']
            # Replace all commas to preserve comma delimited format that the csv.writer module is using with dashes
            manyfeatDesc = ReplaceStrings(manyfeatDesc,",","-")
            manyfeatParent = addFeat['parentId']
            manyfeatProg = addFeat['programId']
            manyfeatIsDel = addFeat['inRecycleBin']
            featArr.append((manyfeatName if manyfeatName else "")+","+(str(manyfeatID) if manyfeatID else "")+","+(manyfeatDesc if manyfeatDesc else "")+","+(str(manyfeatParent) if manyfeatParent else "")+","+(str(manyfeatProg) if manyfeatProg else "")+","+(str(manyfeatIsDel) if manyfeatIsDel else ""))
            # The following 2 lines are good lines to uncomment to see if you are really getting all of the features
            #print (line_count)
    #print('Processed ' + str(line_count) + ' lines')
    return featArr


    
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
####################################################################################################################################################################################
def main():
####################################################################################################################################################################################
# MAIN
    #Collect api server and endpoint. Also collect all of the instance json infomation we need into arrays with CollectUsrMenuItems
    CollectApiInfo()
    #print(instanceurl+apiendpoint)
 
    #Large def, collects infomation on (almost) every endpoint, and collects that info into a comma delimited array
    CollectBasicItems()

    #Features
    if "features" in apiendpoint:
        # Call Feature so that you can build the complete list of Features into an array
        Feature()
        # Call the FeatRoutine that utilizes the array that is created in Features and puts them into a csv file.
        FeatRoutine()
    
    #Capabilities
    if "capabilities" in apiendpoint:
        CapHandler()
    
    #Cities    
    if "cities" in apiendpoint:
        CitHandler()
        
    if "themes" in apiendpoint:
        theme()


####################################################################################################################################################################################
   
    # This section will be deprecated
    #break out into handing each endpoint differently as they will go through iteration in subsequent versions of API
    # #USERS endpoint
    # if "users" in apiendpoint:
    #     print ("From within the users endpoint, you can either retrieve all the users into a spreadsheet, or create a single user  \n")
    #     addUsr = input("Do you want to create a new user? [Y/N]:"+'\n') or "N"
    #     if (addUsr == "Y") or (addUsr == "y"):
    #         CollectUsrMenuItems()
    #         MenuChooser('What Region would you like to put your user into? \n', regArr)
    #         MenuChooser('What City do you want to assign to your user? \n', citArr)
    #         MenuChooser('What Organization do you want to assign to your user? \n', orgArr)
    #         CollectUserInfo()
    #         #CreateUser(UsrEmail,UsrFN,UsrLN)
    #     else:
    #         print ("This script is now going to create a comma delimited file called userlist.csv in the same directory of this script with all of the users listed \n")   
    #         with open('userlist.csv', 'w', newline='') as myfile:
    #             out = csv.writer(myfile,dialect='excel',delimiter=',',quoting=csv.QUOTE_NONE,escapechar=' ')
    #             for eachUsr in usrArr:
    #                 print(eachUsr)
    #                 out.writerow([eachUsr])



    # # #ORGANIZATIONSTRUCTURES endpoint
    # if "organizationstructures" in apiendpoint:
    #     addOrg = input("Do you want to create a new Organization in your instance? If 'No' we will just output a list of the exsiting organizations [Y/N]:"+'\n')
    #     if (addOrg== "Y") or (addOrg == "y"):
    #         print ("Here is a list of all Organizations and thier IDs in Jira Align from your instance \n")
    #         for org in orgArr:
    #             print (org)
    #         # newOrg = input("Please enter the name of the new Organization you would like to create [eg: HR]")
    #         # CreateOrg(newOrg)
    #     else:
    #         print ("Here is a list of all Organizations and thier IDs in Jira Align from your instance \n")
    #         for org in orgArr:
    #             print (org)
        
def theme():
    global themeArr
    themeArr = []
    themes = requests.get(instanceurl + "/themes", auth=BearerAuth(jatoken))
    themeData = themes.json()
    for eachTheme in themeData:
        themeName = eachTheme['title']
        themeID = eachTheme['id']
        themeArr.append(themeName + "," + str(themeID))
        print(themeName)
    return themeArr

    
            
####################################################################################################################################################################################       
if __name__ == "__main__":
    main()     
####################################################################################################################################################################################

