#!/usr/bin/env python3
#
# common.py
#
# All common function used for various example programs.

import json
import time
import csv
from urllib.parse import urlparse

#import subfiles
import cfg
import creds
import workitemparser
import timeboxes
import requests

MAX = 10

def PostToJiraAlign(header, paramData, verify_flag, use_bearer, url = None):
    """Generic method to do a POST to the Jira Align instance, with the specified parameters, and return
        the result of the POST call.

    Args:
        header: The HTTP header to use
        paramData: The data to POST
        verify_flag (bool): Either True or False
        use_bearer (bool): If True, use the BearerAuth token, else use username/token.
        url (string): The URL to use for the POST.  If None, use the default instance + API end point variables defined

    Returns:
        Response
    """
    if url is None:
        # Use the default URL
        url_to_use = instanceurl
    else:
        # Use the given URL
        url_to_use = url

    # If we need to use BearerAuth with Token
    if use_bearer:
        result = requests.post(url = url_to_use, data=json.dumps(paramData), 
                               headers=header, verify=verify_flag, 
                               auth=cfg.BearerAuth(creds.jatoken))
    # Otherwise, use Username/Token auth
    else:
        result = requests.post(url = url_to_use, data=json.dumps(paramData), 
                               headers=header, verify=verify_flag, 
                               auth=(creds.username, creds.jatoken))
    return result

def GetFromJiraAlign(use_bearer, url = None):
    """Generic method to do a GET to the Jira Align instance, with the specified parameters, and return
        the result of the GET call.

    Args:
        use_bearer (bool): If True, use the BearerAuth token, else use username/token.
        url (string): The URL to use for the GET.  If None, use the default instance + API end point variables defined

    Returns:
        Response
    """
    if url is None:
        # Use the default URL
        url_to_use = instanceurl
    else:
        # Use the given URL
        url_to_use = url

    # If we need to use BearerAuth with Token
    if use_bearer:
        result = requests.get(url = url_to_use, auth=cfg.BearerAuth(creds.jatoken))
    # Otherwise, use Username/Token auth
    else:
        result = requests.get(url = url_to_use, auth=(creds.usernamev1, creds.jatokenv1))
    return result

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
    print("Collecting Region info...")
    regions = GetFromJiraAlign(True, cfg.instanceurl + "/regions")
    dataReg = regions.json()
    for eachReg in dataReg:
        #print(eachReg)
        region = eachReg['name']
        regionid = eachReg['id']
        regArr.append("Region Name: " + region + ", Region ID: " + str(regionid))
 
# #GET CITIES
    global citArr
    citArr = []
    print("Collecting City info...")
    cities = GetFromJiraAlign(True, cfg.instanceurl + "/cities")
    dataCit = cities.json()
    for eachCit in dataCit:
        cityID = eachCit['id']
        cityN = eachCit['name']
        citArr.append("City Name: " + cityN + ", City ID: " + str(cityID))
    
    return regArr, citArr

#V2 GET Capabilities
def Capability():
    global capArr
    capArr = []
    print("Collecting Capability info...")
    Capabilities = GetFromJiraAlign(True, cfg.instanceurl + "/capabilities")
    capData = Capabilities.json()   
    for eachCap in capData:
        #print(eachCap['title'])
        capID = eachCap['id']
        capTitle = eachCap['title']
        capArr.append("Capability Name: " + capTitle + ", Capability ID: " + str(capID))
        #capArr.append(str(capID)+","+capTitle)
    return capArr
        
#V2 GET Users
def User():    
    global usrArr
    usrArr = []
    print("Collecting User info...")
    users = GetFromJiraAlign(True, cfg.instanceurl + "/users")
    data = users.json()
    for eachUsr in data:
        fn = eachUsr["firstName"]
        ln = eachUsr["lastName"]
        un = eachUsr['uid']
        em = eachUsr['email']
        usrArr.append("User First Name: " + fn + ", Last Name: " + ln + ", User ID: " + un + ", Email: " + em)
    return usrArr

#V2 GET Programs
def Program():
    global progArr
    progArr = []
    print("Collecting Program info...")
    programs = GetFromJiraAlign(True, cfg.instanceurl + "/programs")
    progData = programs.json()
    for eachProg in progData:
        progName = eachProg['title']
        progID = eachProg['id']
        progArr.append("Program Name: " + progName + ", Program ID: " + str(progID))
    return progArr

#V2 GET Product List for when Products are mandatory on Feature creations
def Product():
    global prodArr
    prodArr = []
    print("Collecting Product info...")
    products = GetFromJiraAlign(True, cfg.instanceurl + "/products")
    prodData = products.json()
    for eachProd in prodData:
        prodName = eachProd['title']
        prodID = eachProd['id']
        prodArr.append("Product Name: " + prodName + ", Product ID: " + str(prodID))
        #print (prodName,prodID)
    return prodArr

#V2 GET Iteration list
def Iterations():
    global iterArr
    iterArr = []
    print("Collecting Iteration info...")
    iters = GetFromJiraAlign(True, cfg.instanceurl + "/iterations")
    data = iters.json()
    line_count = 0
    for iter in data:
        iterationName = iter['title']
        iterationID = iter['releaseId']
        iterArr.append("Iteration Name: " + iterationName + ", Iteration ID: " + str(iterationID))

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
            out.writerow(["title","description","id","parentID","programID","isRecycled"])
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

def PrintXRegions(x):
    """ Output up to x regions to the console.

    Args:
        x: maximum number of regions to output
    """
    i = 1
    size = x
    if len(regArr) < size:
        size = len(regArr)
    print("Here are " + str(size) + " regions defined in Jira Align:")
    for region in regArr:
        print(str(i) + " " + region)
        i = i + 1
        if i > size:
            break

def PrintXCities(x):
    """ Output up to x cities to the console.

    Args:
        x: maximum number of cities to output
    """
    i = 1
    size = x
    if len(citArr) < size:
        size = len(citArr)
    print("Here are " + str(size) + " cities defined in Jira Align:")
    for city in citArr:
        print(str(i) + " " + city)
        i = i + 1
        if i > size:
            break

def PrintXCapabilities(x):
    """ Output up to x capabilities to the console.

    Args:
        x: maximum number of capabilities to output
    """
    i = 1
    size = x
    if len(capArr) < size:
        size = len(capArr)
    print("Here are " + str(size) + " capabilities defined in Jira Align:")
    for capability in capArr:
        print(str(i) + " " + capability)
        i = i + 1
        if i > size:
            break

def PrintXUsers(x):
    """ Output up to x users to the console.

    Args:
        x: maximum number of users to output
    """
    i = 1
    size = x
    if len(usrArr) < size:
        size = len(usrArr)
    print("Here are " + str(size) + " users defined in Jira Align:")
    for user in usrArr:
        print(str(i) + " " + user)
        i = i + 1
        if i > size:
            break

def PrintXPrograms(x):
    """ Output up to x programs to the console.

    Args:
        x: maximum number of programs to output
    """
    i = 1
    size = x
    if len(progArr) < size:
        size = len(progArr)
    print("Here are " + str(size) + " programs defined in Jira Align:")
    for program in progArr:
        print(str(i) + " " + program)
        i = i + 1
        if i > size:
            break

def PrintXProducts(x):
    """ Output up to x products to the console.

    Args:
        x: maximum number of products to output
    """
    i = 1
    size = x
    if len(prodArr) < size:
        size = len(prodArr)
    print("Here are " + str(size) + " products defined in Jira Align:")
    for product in prodArr:
        print(str(i) + " " + product)
        i = i + 1
        if i > size:
            break

def PrintXIterations(x):
    """ Output up to x iterations to the console.

    Args:
        x: maximum number of iterations to output
    """
    i = 1
    size = x
    if len(iterArr) < size:
        size = len(iterArr)
    print("Here are " + str(size) + " iterations defined in Jira Align:")
    for iteration in iterArr:
        print(str(i) + " " + iteration)
        i = i + 1
        if i > size:
            break

def GetAllRegions():
    """ Get all Region information and return to the caller.

        Returns: All the details for each region in a list of objects.
    """
    regArr = []
    print("Collecting all Region info...")
    regions = GetFromJiraAlign(True, cfg.instanceurl + "/regions")
    dataReg = regions.json()
    for eachReg in dataReg:
        itemDict = {}
        itemDict['id'] = eachReg['id']
        itemDict['name'] = eachReg['name']
        if eachReg['lastUpdatedDate'] is not None:
            itemDict['lastUpdatedDate'] = eachReg['lastUpdatedDate']
        # Don't save the self field, since it will be generated during creation
        regArr.append(itemDict)
    return regArr

# APIv2 doesn't seem to support this.
def GetAllCountries():
    """ Get all Countries information and return to the caller.

        Returns: All the details for each country in a list of objects.
    """
    countryArr = []
    print("Collecting all Country info...")
    countries = GetFromJiraAlign(True, cfg.instanceurl + "/countries")
    dataCountry = countries.json()
    for eachCountry in dataCountry:
        itemDict = {}
        itemDict['id'] = eachCountry['id']
        itemDict['name'] = eachCountry['name']
        if eachCountry['lastUpdatedDate'] is not None:
            itemDict['lastUpdatedDate'] = eachCountry['lastUpdatedDate']
        # Don't save the self field, since it will be generated during creation
        countryArr.append(itemDict)
    return countryArr

def GetAllCities():
    """ Get all Cities information and return to the caller.

        Returns: All the details for each city in a list of objects.
    """
    cityArr = []
    print("Collecting all City info...")
    cities = GetFromJiraAlign(True, cfg.instanceurl + "/cities")
    dataCity = cities.json()
    for eachCity in dataCity:
        itemDict = {}
        itemDict['id'] = eachCity['id']
        itemDict['name'] = eachCity['name']
        itemDict['regionId'] = eachCity['regionId']
        itemDict['applyTimeTracking'] = eachCity['applyTimeTracking']
        if eachCity['lastUpdatedDate'] is not None:
            itemDict['lastUpdatedDate'] = eachCity['lastUpdatedDate']
        # Don't save the self field, since it will be generated during creation
        cityArr.append(itemDict)
    return cityArr

def GetAllProducts():
    """ Get all Products information and return to the caller.

        Returns: All the details for each product in a list of objects.
    """
    productArr = []
    print("Collecting all Product info...")
    products = GetFromJiraAlign(True, cfg.instanceurl + "/products")
    dataProduct = products.json()
    for eachProduct in dataProduct:
        itemDict = {}
        itemDict['id'] = eachProduct['id']
        itemDict['title'] = eachProduct['title']
        itemDict['shortName'] = eachProduct['shortName']
        itemDict['isActive'] = eachProduct['isActive']
        itemDict['parentProductId'] = eachProduct['parentProductId']
        itemDict['divisionId'] = eachProduct['divisionId']
        itemDict['personaIds'] = eachProduct['personaIds']
        itemDict['competitorIds'] = eachProduct['competitorIds']
        itemDict['roadmapSnapshotIds'] = eachProduct['roadmapSnapshotIds']
        if eachProduct['lastUpdatedDate'] is not None:
            itemDict['lastUpdatedDate'] = eachProduct['lastUpdatedDate']
        # Don't save the self field, since it will be generated during creation
        productArr.append(itemDict)
    return productArr

def GetAllPrograms():
    """ Get all Programs information and return to the caller.

        Returns: All the details for each program in a list of objects.
    """
    programArr = []
    print("Collecting all Program info...")
    programs = GetFromJiraAlign(True, cfg.instanceurl + "/programs")
    dataProgram = programs.json()
    for eachProgram in dataProgram:
        itemDict = {}
        itemDict['id'] = eachProgram['id']
        itemDict['title'] = eachProgram['title']
        itemDict['portfolioId'] = eachProgram['portfolioId']
        itemDict['solutionId'] = eachProgram['solutionId']
        itemDict['isSolution'] = eachProgram['isSolution']
        itemDict['teamId'] = eachProgram['teamId']
        itemDict['teamDescription'] = eachProgram['teamDescription']
        itemDict['scoreCardId'] = eachProgram['scoreCardId']
        itemDict['intakeFormId'] = eachProgram['intakeFormId']
        itemDict['regionId'] = eachProgram['regionId']
        if eachProgram['caseDevelopmentId'] is not None:
            itemDict['caseDevelopmentId'] = eachProgram['caseDevelopmentId']
        if eachProgram['lastUpdatedDate'] is not None:
            itemDict['lastUpdatedDate'] = eachProgram['lastUpdatedDate']
        # Don't save the self field, since it will be generated during creation
        programArr.append(itemDict)
    return programArr

def GetAllUsers():
    """ Get all Users information and return to the caller.

        Returns: All the details for each user in a list of objects.
    """
    userArr = []
    print("Collecting all User info...")
    users = GetFromJiraAlign(True, cfg.instanceurl + "/users")
    dataUsers = users.json()
    for eachUser in dataUsers:
        itemDict = {}
        itemDict['id'] = eachUser['id']
        itemDict['uid'] = eachUser['uid']
        itemDict['firstName'] = eachUser['firstName']
        itemDict['lastName'] = eachUser['lastName']
        itemDict['fullName'] = eachUser['fullName']
        itemDict['email'] = eachUser['email']
        itemDict['createDate'] = eachUser['createDate']
        itemDict['isExternal'] = eachUser['isExternal']
        itemDict['externalId'] = eachUser['externalId']
        itemDict['isLocked'] = eachUser['isLocked']
        itemDict['status'] = eachUser['status']
        itemDict['employeeId'] = eachUser['employeeId']
        itemDict['regionId'] = eachUser['regionId']
        itemDict['title'] = eachUser['title']
        itemDict['roleId'] = eachUser['roleId']
        itemDict['cityId'] = eachUser['cityId']
        itemDict['costCenterId'] = eachUser['costCenterId']
        itemDict['viewPublicErs'] = eachUser['viewPublicErs']
        itemDict['employeeClassification'] = eachUser['employeeClassification']
        itemDict['includeHours'] = eachUser['includeHours']
        itemDict['teams'] = eachUser['teams']
        if eachUser['isComplianceManager'] is not None:
            itemDict['isComplianceManager'] = eachUser['isComplianceManager']
        if eachUser['isUserManager'] is not None:
            itemDict['isUserManager'] = eachUser['isUserManager']
        if eachUser['managerId'] is not None:
            itemDict['managerId'] = eachUser['managerId']
        if eachUser['holidayRegionId'] is not None:
            itemDict['holidayRegionId'] = eachUser['holidayRegionId']
        if eachUser['isTimeTracking'] is not None:
            itemDict['isTimeTracking'] = eachUser['isTimeTracking']
            itemDict['timeTrackingRoles'] = eachUser['timeTrackingRoles']
            itemDict['timeTrackingStartDate'] = eachUser['timeTrackingStartDate']
            itemDict['timeApproverId'] = eachUser['timeApproverId']
        if eachUser['company'] is not None:
            itemDict['company'] = eachUser['company']
            itemDict['companyId'] = eachUser['companyId']
            itemDict['divisionId'] = eachUser['divisionId']
        if eachUser['notes'] is not None:
            itemDict['notes'] = eachUser['notes']
        if eachUser['timeZone'] is not None:
            itemDict['timeZone'] = eachUser['timeZone']
        if eachUser['userStartDate'] is not None:
            itemDict['userStartDate'] = eachUser['userStartDate']
        if eachUser['userEndDate'] is not None:
            itemDict['userEndDate'] = eachUser['userEndDate']
        if eachUser['connectorId'] is not None:
            itemDict['connectorId'] = eachUser['connectorId']
        if eachUser['lastUpdatedDate'] is not None:
            itemDict['lastUpdatedDate'] = eachUser['lastUpdatedDate']
        # Don't save the self field, since it will be generated during creation
        userArr.append(itemDict)
    return userArr

def GetAllIterations():
    """ Get all Iterations information and return to the caller.

        Returns: All the details for each iteration in a list of objects.
    """
    iterationsArr = []
    print("Collecting all Iteration info...")
    iterations = GetFromJiraAlign(True, cfg.instanceurl + "/iterations")
    dataIterations = iterations.json()
    for eachIteration in dataIterations:
        itemDict = {}
        itemDict['id'] = eachIteration['id']
        itemDict['releaseId'] = eachIteration['releaseId']
        itemDict['title'] = eachIteration['title']
        itemDict['shortName'] = eachIteration['shortName']
        itemDict['schedule'] = eachIteration['schedule']
        itemDict['state'] = eachIteration['state']
        itemDict['teamId'] = eachIteration['teamId']
        itemDict['maxAllocation'] = eachIteration['maxAllocation']
        itemDict['color'] = eachIteration['color']
        itemDict['isLocked'] = eachIteration['isLocked']
        itemDict['defectAllocation'] = eachIteration['defectAllocation']
        itemDict['programId'] = eachIteration['programId']
        itemDict['regionId'] = eachIteration['regionId']
        itemDict['type'] = eachIteration['type']
        if eachIteration['beginDate'] is not None:
            itemDict['beginDate'] = eachIteration['beginDate']
        if eachIteration['endDate'] is not None:
            itemDict['endDate'] = eachIteration['endDate']
        if eachIteration['actualEndDate'] is not None:
            itemDict['actualEndDate'] = eachIteration['actualEndDate']
        if eachIteration['description'] is not None:
            itemDict['description'] = eachIteration['description']
        if eachIteration['overrideVelocity'] is not None:
            itemDict['overrideVelocity'] = eachIteration['overrideVelocity']
        if eachIteration['createDate'] is not None:
            itemDict['createDate'] = eachIteration['createDate']
        if eachIteration['goal'] is not None:
            itemDict['goal'] = eachIteration['goal']
        if eachIteration['anchorSprintId'] is not None:
            itemDict['anchorSprintId'] = eachIteration['anchorSprintId']
        if eachIteration['regressionHours'] is not None:
            itemDict['regressionHours'] = eachIteration['regressionHours']
        if eachIteration['lastUpdatedDate'] is not None:
            itemDict['lastUpdatedDate'] = eachIteration['lastUpdatedDate']
        # Don't save the self field, since it will be generated during creation
        iterationsArr.append(itemDict)
    return iterationsArr

def GetAllSnapshots():
    """ Get all Snapshots information and return to the caller.

        Returns: All the details for each snapshot in a list of objects.
    """
    snapshotArr = []
    print("Collecting all Snapshot info...")
    snapshots = GetFromJiraAlign(True, cfg.instanceurl + "/snapshots")
    dataSnapshots = snapshots.json()
    for eachSnapshot in dataSnapshots:
        itemDict = {}
        itemDict['id'] = eachSnapshot['id']
        itemDict['title'] = eachSnapshot['title']
        itemDict['description'] = eachSnapshot['description']
        itemDict['ownerId'] = eachSnapshot['ownerId']
        itemDict['horizonPercentage1'] = eachSnapshot['horizonPercentage1']
        itemDict['horizonPercentage2'] = eachSnapshot['horizonPercentage2']
        itemDict['horizonPercentage3'] = eachSnapshot['horizonPercentage3']
        if eachSnapshot['startDate'] is not None:
            itemDict['startDate'] = eachSnapshot['startDate']
        if eachSnapshot['endDate'] is not None:
            itemDict['endDate'] = eachSnapshot['endDate']
        if eachSnapshot['budget'] is not None:
            itemDict['budget'] = eachSnapshot['budget']
        if eachSnapshot['productIds'] is not None:
            itemDict['productIds'] = eachSnapshot['productIds']
        if eachSnapshot['releaseIds'] is not None:
            itemDict['releaseIds'] = eachSnapshot['releaseIds']
        if eachSnapshot['divisionIds'] is not None:
            itemDict['divisionIds'] = eachSnapshot['divisionIds']
        if eachSnapshot['enableSnapshotNotification'] is not None:
            itemDict['enableSnapshotNotification'] = eachSnapshot['enableSnapshotNotification']
        if eachSnapshot['enableStrategyNotification'] is not None:
            itemDict['enableStrategyNotification'] = eachSnapshot['enableStrategyNotification']
        if eachSnapshot['teamMemberIds'] is not None:
            itemDict['teamMemberIds'] = eachSnapshot['teamMemberIds']
        # Don't save the self field, since it will be generated during creation
        snapshotArr.append(itemDict)
    return snapshotArr

def GetAllThemes():
    """ Get all Themes information and return to the caller.

        Returns: All the details for each theme in a list of objects.
    """
    themeArr = []
    print("Collecting all Theme info...")
    themes = GetFromJiraAlign(True, cfg.instanceurl + "/themes")
    dataThemes = themes.json()
    for eachTheme in dataThemes:
        itemDict = {}
        itemDict['id'] = eachTheme['id']
        itemDict['title'] = eachTheme['title']
        itemDict['isActive'] = eachTheme['isActive']
        itemDict['strategic'] = eachTheme['strategic']
        itemDict['isMajor'] = eachTheme['isMajor']
        itemDict['state'] = eachTheme['state']
        itemDict['description'] = eachTheme['description']
        itemDict['programIds'] = eachTheme['programIds']
        itemDict['releaseIds'] = eachTheme['releaseIds']
        itemDict['reportColor'] = eachTheme['reportColor']
        itemDict['goalId'] = eachTheme['goalId']
        itemDict['plannedBudget'] = eachTheme['plannedBudget']
        if eachTheme['themeGroupId'] is not None:
            itemDict['themeGroupId'] = eachTheme['themeGroupId']
        if eachTheme['externalId'] is not None:
            itemDict['externalId'] = eachTheme['externalId']
        if eachTheme['developmentalStepId'] is not None:
            eachTheme['developmentalStepId'] = eachTheme['developmentalStepId']
        if eachTheme['operationalStepId'] is not None:
            itemDict['operationalStepId'] = eachTheme['operationalStepId']
        if eachTheme['externalProject'] is not None:
            itemDict['externalProject'] = eachTheme['externalProject']
        if eachTheme['externalKey'] is not None:
            itemDict['externalKey'] = eachTheme['externalKey']
        if eachTheme['connectorId'] is not None:
            itemDict['connectorId'] = eachTheme['connectorId']
        if eachTheme['createdBy'] is not None:
            itemDict['createdBy'] = eachTheme['createdBy']
        if eachTheme['createDate'] is not None:
            itemDict['createDate'] = eachTheme['createDate']
        if eachTheme['owner'] is not None:
            itemDict['owner'] = eachTheme['owner']
        if eachTheme['targetCompletionDate'] is not None:
            itemDict['targetCompletionDate'] = eachTheme['targetCompletionDate']
        if eachTheme['startInitiationDate'] is not None:
            itemDict['startInitiationDate'] = eachTheme['startInitiationDate']
        if eachTheme['portfolioAskDate'] is not None:
            itemDict['portfolioAskDate'] = eachTheme['portfolioAskDate']
        if eachTheme['ctext1'] is not None:
            itemDict['ctext1'] = eachTheme['ctext1']
        if eachTheme['ctext2'] is not None:
            itemDict['ctext2'] = eachTheme['ctext2']
        if eachTheme['carea1'] is not None:
            itemDict['carea1'] = eachTheme['carea1']
        if eachTheme['cdrop1'] is not None:
            itemDict['cdrop1'] = eachTheme['cdrop1']
        if eachTheme['cdrop2'] is not None:
            itemDict['cdrop2'] = eachTheme['cdrop2']
        if eachTheme['cdrop3'] is not None:
            itemDict['cdrop3'] = eachTheme['cdrop3']
        if eachTheme['cdrop4'] is not None:
            itemDict['cdrop4'] = eachTheme['cdrop4']
        if eachTheme['cdrop5'] is not None:
            itemDict['cdrop5'] = eachTheme['cdrop5']
        if eachTheme['customFields'] is not None:
            itemDict['customFields'] = eachTheme['customFields']
        if eachTheme['lastUpdatedDate'] is not None:
            itemDict['lastUpdatedDate'] = eachTheme['lastUpdatedDate']
        # Don't save the self field, since it will be generated during creation
        themeArr.append(itemDict)
    return themeArr

def GetAllGoals():
    """ Get all Goals information and return to the caller.

        Returns: All the details for each goal in a list of objects.
    """
    goalArr = []
    print("Collecting all Goal info...")
    goals = GetFromJiraAlign(True, cfg.instanceurl + "/goals")
    dataGoals = goals.json()
    for eachGoal in dataGoals:
        itemDict = {}
        itemDict['id'] = eachGoal['id']
        itemDict['type'] = eachGoal['type']
        itemDict['description'] = eachGoal['description']
        itemDict['parentId'] = eachGoal['parentId']
        itemDict['createDate'] = eachGoal['createDate']
        itemDict['ownerId'] = eachGoal['ownerId']
        if eachGoal['feasibility'] is not None:
            itemDict['feasibility'] = eachGoal['feasibility']
        if eachGoal['importance'] is not None:
            itemDict['importance'] = eachGoal['importance']
        if eachGoal['divisionId'] is not None:
            itemDict['divisionId'] = eachGoal['divisionId']
        if eachGoal['marketAssessment'] is not None:
            itemDict['marketAssessment'] = eachGoal['marketAssessment']
        if eachGoal['reference'] is not None:
            itemDict['reference'] = eachGoal['reference']
        if eachGoal['snapshotIds'] is not None:
            itemDict['snapshotIds'] = eachGoal['snapshotIds']
        if eachGoal['allocations'] is not None:
            itemDict['allocations'] = eachGoal['allocations']
        # Don't save the self field, since it will be generated during creation
        goalArr.append(itemDict)
    return goalArr

def GetAllObjectives():
    """ Get all Objectives information and return to the caller.

        Returns: All the details for each objective in a list of objects.
    """
    objectiveArr = []
    print("Collecting all Objectives info...")
    objectives = GetFromJiraAlign(True, cfg.instanceurl + "/objectives")
    dataObjectives = objectives.json()
    for eachObjective in dataObjectives:
        itemDict = {}
        itemDict['id'] = eachObjective['id']
        itemDict['tier'] = eachObjective['tier']
        itemDict['programId'] = eachObjective['programId']
        itemDict['type'] = eachObjective['type']
        itemDict['isBlocked'] = eachObjective['isBlocked']
        itemDict['ownerId'] = eachObjective['ownerId']
        itemDict['name'] = eachObjective['name']
        itemDict['description'] = eachObjective['description']
        if eachObjective['createDate'] is not None:
            itemDict['createDate'] = eachObjective['createDate']
        if eachObjective['status'] is not None:
            itemDict['status'] = eachObjective['status']
        if eachObjective['notes'] is not None:
            itemDict['notes'] = eachObjective['notes']
        if eachObjective['startInitiationDate'] is not None:
            itemDict['startInitiationDate'] = eachObjective['startInitiationDate']
        if eachObjective['endDate'] is not None:
            itemDict['endDate'] = eachObjective['endDate']
        if eachObjective['category'] is not None:
            itemDict['category'] = eachObjective['category']
        if eachObjective['targetSyncSprintId'] is not None:
            itemDict['targetSyncSprintId'] = eachObjective['targetSyncSprintId']
        if eachObjective['plannedValue'] is not None:
            itemDict['plannedValue'] = eachObjective['plannedValue']
        if eachObjective['deliveredValue'] is not None:
            itemDict['deliveredValue'] = eachObjective['deliveredValue']
        if eachObjective['themeId'] is not None:
            itemDict['themeId'] = eachObjective['themeId']
        if eachObjective['blockedReason'] is not None:
            itemDict['blockedReason'] = eachObjective['blockedReason']
        if eachObjective['lastUpdatedDate'] is not None:
            itemDict['lastUpdatedDate'] = eachObjective['lastUpdatedDate']
        if eachObjective['lastUpdatedBy'] is not None:
            itemDict['lastUpdatedBy'] = eachObjective['lastUpdatedBy']
        if eachObjective['targetCompletionDate'] is not None:
            itemDict['targetCompletionDate'] = eachObjective['targetCompletionDate']
        if eachObjective['portfolioAskDate'] is not None:
            itemDict['portfolioAskDate'] = eachObjective['portfolioAskDate']
        if eachObjective['health'] is not None:
            itemDict['health'] = eachObjective['health']
        if eachObjective['parentId'] is not None:
            itemDict['parentId'] = eachObjective['parentId']
        if eachObjective['score'] is not None:
            itemDict['score'] = eachObjective['score']
        if eachObjective['portfolioId'] is not None:
            itemDict['portfolioId'] = eachObjective['portfolioId']
        if eachObjective['goalId'] is not None:
            itemDict['goalId'] = eachObjective['goalId']
        if eachObjective['solutionId'] is not None:
            itemDict['solutionId'] = eachObjective['solutionId']
        if eachObjective['notificationStartDate'] is not None:
            itemDict['notificationStartDate'] = eachObjective['notificationStartDate']
        if eachObjective['notificationFrequency'] is not None:
            itemDict['notificationFrequency'] = eachObjective['notificationFrequency']
        if eachObjective['reference'] is not None:
            itemDict['reference'] = eachObjective['reference']
        if eachObjective['programIds'] is not None:
            itemDict['programIds'] = eachObjective['programIds']
        if eachObjective['releaseIds'] is not None:
            itemDict['releaseIds'] = eachObjective['releaseIds']
        if eachObjective['featureIds'] is not None:
            itemDict['featureIds'] = eachObjective['featureIds']
        if eachObjective['impedimentIds'] is not None:
            itemDict['impedimentIds'] = eachObjective['impedimentIds']
        if eachObjective['riskIds'] is not None:
            itemDict['riskIds'] = eachObjective['riskIds']
        if eachObjective['dependencyIds'] is not None:
            itemDict['dependencyIds'] = eachObjective['dependencyIds']
        if eachObjective['customFields'] is not None:
            itemDict['customFields'] = eachObjective['customFields']
        if eachObjective['teamIds'] is not None:
            itemDict['teamIds'] = eachObjective['teamIds']
        # Don't save the self field, since it will be generated during creation
        objectiveArr.append(itemDict)
    return objectiveArr

def GetAllReleases():
    """ Get all Releases information and return to the caller.

        Returns: All the details for each release in a list of objects.
    """
    releaseArr = []
    print("Collecting all Releases info...")
    releases = GetFromJiraAlign(True, cfg.instanceurl + "/releases")
    dataReleases = releases.json()
    for eachRelease in dataReleases:
        itemDict = {}
        itemDict['id'] = eachRelease['id']
        itemDict['title'] = eachRelease['title']
        itemDict['shortName'] = eachRelease['shortName']
        itemDict['type'] = eachRelease['type']
        itemDict['status'] = eachRelease['status']
        itemDict['description'] = eachRelease['description']
        if eachRelease['createDate'] is not None:
            itemDict['createDate'] = eachRelease['createDate']
        if eachRelease['startDate'] is not None:
            itemDict['startDate'] = eachRelease['startDate']
        if eachRelease['endDate'] is not None:
            itemDict['endDate'] = eachRelease['endDate']
        if eachRelease['releaseNumber'] is not None:
            itemDict['releaseNumber'] = eachRelease['releaseNumber']
        # Don't save the self field, since it will be generated during creation
        releaseArr.append(itemDict)
    return releaseArr

def ExtractItemData(itemType, sourceItem, extractedData):
    """ Extract all applicable fields from the source item and add them to the extracted
        data, based on item type.

    Args:
        itemType: Which type of work the sourceItem is: epics, features, stories, defects, tasks
        sourceItem: Full set of data for this item from Jira Align
        extractedData: All the data that needs to be saved from this sourceItem
    """
    # Common fields for all item types
    extractedData['itemtype'] = itemType
    extractedData['title'] = sourceItem['title']
    if sourceItem['description'] is not None:
        extractedData['description'] = sourceItem['description']
    extractedData['id'] = sourceItem['id']
    extractedData['state'] = sourceItem['state']
    if sourceItem['createDate'] is not None:
        extractedData['createDate'] = sourceItem['createDate']
    
    # Specific fields to extract for each item type
    if itemType == "epics":
        extractedData['themeId'] = sourceItem['themeId']
        extractedData['primaryProgramId'] = sourceItem['primaryProgramId']
        extractedData['type'] = sourceItem['type']
        if sourceItem['epicObjectId'] is not None:
            extractedData['epicObjectId'] = sourceItem['epicObjectId']
        if sourceItem['themeId'] is not None:
            extractedData['themeId'] = sourceItem['themeId']
        if sourceItem['primaryProgramId'] is not None:
            extractedData['primaryProgramId'] = sourceItem['primaryProgramId']
        if sourceItem['points'] is not None:
            extractedData['points'] = sourceItem['points']
        if sourceItem['acceptedDate'] is not None:
            extractedData['acceptedDate'] = sourceItem['acceptedDate']
    elif itemType == "features":
        extractedData['parentId'] = sourceItem['parentId']
        extractedData['primaryProgramId'] = sourceItem['primaryProgramId']
        if sourceItem['productId'] is not None:
            extractedData['productId'] = sourceItem['productId']
        if sourceItem['parentId'] is not None:
            extractedData['parentId'] = sourceItem['parentId']
        if sourceItem['themeId'] is not None:
            extractedData['themeId'] = sourceItem['themeId']
        if sourceItem['primaryProgramId'] is not None:
            extractedData['primaryProgramId'] = sourceItem['primaryProgramId']
        if sourceItem['points'] is not None:
            extractedData['points'] = sourceItem['points']
        if sourceItem['acceptedDate'] is not None:
            extractedData['acceptedDate'] = sourceItem['acceptedDate']
    elif itemType == "stories":
        extractedData['programId'] = sourceItem['programId']
        if sourceItem['featureId'] is not None:
            extractedData['featureId'] = sourceItem['featureId']
        if sourceItem['releaseId'] is not None:
            extractedData['releaseId'] = sourceItem['releaseId']
        if sourceItem['valuePoints'] is not None:
            extractedData['valuePoints'] = sourceItem['valuePoints']
        if sourceItem['effortPoints'] is not None:
            extractedData['effortPoints'] = sourceItem['effortPoints']
        if sourceItem['connectorId'] is not None:
            extractedData['connectorId'] = sourceItem['connectorId']
        if sourceItem['acceptedDate'] is not None:
            extractedData['acceptedDate'] = sourceItem['acceptedDate']
    elif itemType == "defects":
        extractedData['storyId'] = sourceItem['storyId']
        extractedData['programId'] = sourceItem['programId']
        if sourceItem['closeDate'] is not None:
            extractedData['closeDate'] = sourceItem['closeDate']
        if sourceItem['iterationId'] is not None:
            extractedData['iterationId'] = sourceItem['iterationId']
        if sourceItem['teamId'] is not None:
            extractedData['teamId'] = sourceItem['teamId']
        if sourceItem['pointsEstimate'] is not None:
            extractedData['pointsEstimate'] = sourceItem['pointsEstimate']
        if sourceItem['hoursEstimate'] is not None:
            extractedData['hoursEstimate'] = sourceItem['hoursEstimate']
        if sourceItem['connectorId'] is not None:
            extractedData['connectorId'] = sourceItem['connectorId']
    elif itemType == "tasks":
        extractedData['storyId'] = sourceItem['storyId']
        extractedData['type'] = sourceItem['type']
        if sourceItem['effortHours'] is not None:
            extractedData['effortHours'] = sourceItem['effortHours']
        if sourceItem['totalHours'] is not None:
            extractedData['totalHours'] = sourceItem['totalHours']
        if sourceItem['lastUpdatedDate'] is not None:
            extractedData['lastUpdatedDate'] = sourceItem['lastUpdatedDate']
        if sourceItem['completedDate'] is not None:
            extractedData['completedDate'] = sourceItem['completedDate']

def ReadAllItems(which, maxToRead):
    """ Read in all work items of the given type (Epic, Feature, Story, etc.) and 
        return selected fields of them to the caller.  This is NOT a complete dump of all data.
        Any work items that are deleted/in recycle bin are skipped.

    Args:
        which: Which type of work items to retrieve.  
               Valid values are: epics, capabilities, features, stories, defects, tasks

        maxToRead: Maximum number of entries to read in.
    """
    print("Collecting up to " + str(maxToRead) + " items of type " + which + "...")
    itemArr = []

    # Get the first set of data, which may be everything or may not be
    items = GetFromJiraAlign(True, cfg.instanceurl + "/" + which)
    Data = items.json()
    line_count = 0
    # Starting point for skipping is to go to the next 100..
    skip = 100

    while Data != None:
        for eachWorkItem in Data:
            itemIsDel = eachWorkItem['isRecycled']
            # ONLY Take items that are not in the recycle bin/deleted
            if itemIsDel is not None or itemIsDel is True:
                continue;
            thisItem = {}
            ExtractItemData(which, eachWorkItem, thisItem)
            line_count += 1
            itemArr.append(thisItem)

        # If we got all the items, the return what we have
        if len(Data) < 100:
            break
        # If we have read in as many as request (or more) then return
        if len(itemArr) >= maxToRead:
            break

        # Otherwise, there are more items to get, so get the next 100
        moreItems = GetFromJiraAlign(True, cfg.instanceurl + "/" + which + "?&$skip=" + str(skip))
        Data = moreItems.json()
        skip += 100

    print('Loaded ' + str(line_count) + " items of type " + which)
    return itemArr
