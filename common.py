#!/usr/bin/env python3
#
# common.py
#
# All common function used for various example programs.

import json
import time
import csv
from urllib.parse import urlparse

import cfg
import creds
import workitemparser
import requests

# Set to True to see additional debug info on exact URLs used
DEBUG = False
# Set to True to use hardcoded values for API Endpoint and Instance URL
# Set to False to prompt each time
USE_DEFAULTS = False

def PatchToJiraAlign(header, paramData, verify_flag, use_bearer, url = None):
    """Generic method to do a PATCH to the Jira Align instance, with the specified parameters, and return
        the result of the PATCH call.

    Args:
        header: The HTTP header to use
        paramData: The data to PATCH
        verify_flag (bool): Either True or False
        use_bearer (bool): If True, use the BearerAuth token, else use username/token.
        url (string): The URL to use for the PATCH.  If None, use the default instance + API end point variables defined

    Returns:
        Response
    """
    if url is None:
        # Use the default URL
        url_to_use = cfg.instanceurl
    else:
        # Use the given URL
        url_to_use = url
    if DEBUG == True:
        print("Headers: " + header)
        print("Data: " + paramData)
        print("URL: " + url_to_use)
    # If we need to use BearerAuth with Token
    if use_bearer:
        result = requests.patch(url = url_to_use, data=json.dumps(paramData),
                               headers=header, 
                               verify=verify_flag, 
                               auth=cfg.BearerAuth(creds.jatoken))
    # Otherwise, use Username/Token auth
    else:
        result = requests.patch(url = url_to_use, data=json.dumps(paramData),
                               headers=header, verify=verify_flag, 
                               auth=(creds.username, creds.jatoken))
    return result

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
        url_to_use = cfg.instanceurl
    else:
        # Use the given URL
        url_to_use = url
    if DEBUG == True:
        print("URL: " + url_to_use)
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
        url_to_use = cfg.instanceurl
    else:
        # Use the given URL
        url_to_use = url
    if DEBUG == True:
        print("URL: " + url_to_use)

    # If we need to use BearerAuth with Token
    if use_bearer:
        result = requests.get(url = url_to_use, auth=cfg.BearerAuth(creds.jatoken))
    # Otherwise, use Username/Token auth
    else:
        result = requests.get(url = url_to_use, auth=(creds.usernamev1, creds.jatokenv1))
    return result

# This collects instance details like the url and the endpoint you want to target
def CollectApiInfo():
    print("Instance URL is normally something like:  https://foo.jiraalign.com")
    print("API Endpoint is normally: /")
    if USE_DEFAULTS == True:
        cfg.apiendpoint = "/"
        cfg.instanceurl = "https://foo.jiraalign.com"
    else:
        cfg.apiendpoint = input("Enter the api endpoint for your instance in following format EG. ""cities"". It is very important that you spell this endpoint correctly. Please refer to the api documents E.G https://cprime.agilecraft.com/api-docs/public/ for the apiendpoints available : ")
        #print(apiendpoint)
        cfg.instanceurl = input("Enter the url for your instance in following format EG. ""https://foo.agilecraft.com"" : ")
        ChkInput = input("Is this your correct instance and endpoint you want to work with?  " + cfg.instanceurl + " : " + cfg.apiendpoint + "  " + "\n")
        if (ChkInput == "N") or (ChkInput == "n"):
            CollectApiInfo()

    cfg.abouturl = cfg.instanceurl + "/About"
    cfg.instanceurl = cfg.instanceurl + "/rest/align/api/2" ##### Mess with these couple of lines, and break all of the other defs! 
    cfg.apiendpoint = "/" + cfg.apiendpoint.lower()
    cfg.api1instance = urlparse(cfg.instanceurl)
    cfg.api1instance = cfg.api1instance.scheme + "://" + cfg.api1instance.netloc
    cfg.api1instance = cfg.api1instance + "/api"
    print(cfg.instanceurl, cfg.api1instance)

    # Get the About page from Jira Align, and parse out the Jira Align version number from it
    aboutInfo = GetFromJiraAlign(False, cfg.abouturl)
    if DEBUG == True:
        print(aboutInfo.text)
    # This assumes a specific format/length of the JA version
    start = aboutInfo.text.find("data-version") + 14
    end = start + 14
    cfg.jaVersion = aboutInfo.text[start:end]
    
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
        itemDict['code'] = eachReg['code']
        itemDict['flag'] = eachReg['flag']
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
        itemDict['applyTimeTracking'] = eachCity['applyTimeTracking']
        itemDict['image'] = eachCity['image']
        itemDict['name'] = eachCity['name']
        itemDict['regionId'] = eachCity['regionId']
        if eachCity['lastUpdatedDate'] is not None:
            itemDict['lastUpdatedDate'] = eachCity['lastUpdatedDate']
        # Don't save the self field, since it will be generated during creation
        cityArr.append(itemDict)
    return cityArr

def GetAllConnectorBoards():
    """ Get all Connector Board information and return to the caller.

        Returns: All the details for each connector board in a list of objects.
    """
    boardArr = []
    print("Collecting all Connector Board info...")
    boards = GetFromJiraAlign(True, cfg.instanceurl + "/connectors/1/boards")
    dataBoard = boards.json()
    for eachBoard in dataBoard:
        itemDict = {}
        itemDict['id'] = eachBoard['id']
        itemDict['areSprintsEnabled'] = eachBoard['areSprintsEnabled']
        itemDict['boardId'] = eachBoard['boardId']
        itemDict['boardName'] = eachBoard['boardName']
        itemDict['connectorId'] = eachBoard['connectorId']
        itemDict['createdBy'] = eachBoard['createdBy']
        itemDict['createDate'] = eachBoard['createDate']
        if eachBoard['errorMessage'] is not None:
            itemDict['errorMessage'] = eachBoard['errorMessage']
        itemDict['originSprints'] = eachBoard['originSprints']
        itemDict['programId'] = eachBoard['programId']
        itemDict['teamId'] = eachBoard['teamId']
        itemDict['teamName'] = eachBoard['teamName']
        if eachBoard['lastUpdatedBy'] is not None:
            itemDict['lastUpdatedBy'] = eachBoard['lastUpdatedBy']
        if eachBoard['lastUpdatedDate'] is not None:
            itemDict['lastUpdatedDate'] = eachBoard['lastUpdatedDate']
        # Don't save the self field, since it will be generated during creation
        boardArr.append(itemDict)
    return boardArr
    
def GetAllConnectorPriorities():
    """ Get all Connector Priority information and return to the caller.

        Returns: All the details for each connector priority in a list of objects.
    """
    prioritiesArr = []
    print("Collecting all Connector Priority info...")
    priorities = GetFromJiraAlign(True, cfg.instanceurl + "/connectors/1/priorities")
    dataPriority = priorities.json()
    for eachPriority in dataPriority:
        itemDict = {}
        itemDict['id'] = eachPriority['id']
        itemDict['connectorId'] = eachPriority['connectorId']
        if eachPriority['createdBy'] is not None:
            itemDict['createdBy'] = eachPriority['createdBy']
        if eachPriority['createDate'] is not None:
            itemDict['createDate'] = eachPriority['createDate']
        itemDict['itemTypeId'] = eachPriority['itemTypeId']
        itemDict['jiraPriorityId'] = eachPriority['jiraPriorityId']
        itemDict['jiraPriorityName'] = eachPriority['jiraPriorityName']
        itemDict['priorityId'] = eachPriority['priorityId']
        if eachPriority['lastUpdatedBy'] is not None:
            itemDict['lastUpdatedBy'] = eachPriority['lastUpdatedBy']
        if eachPriority['lastUpdatedDate'] is not None:
            itemDict['lastUpdatedDate'] = eachPriority['lastUpdatedDate']
        # Don't save the self field, since it will be generated during creation
        prioritiesArr.append(itemDict)
    return prioritiesArr
    
def GetAllConnectorProjects():
    """ Get all Connector Project information and return to the caller.

        Returns: All the details for each connector project in a list of objects.
    """
    projectsArr = []
    print("Collecting all Connector Project info...")
    projects = GetFromJiraAlign(True, cfg.instanceurl + "/connectors/1/projects")
    dataProject = projects.json()
    for eachProject in dataProject:
        itemDict = {}
        itemDict['id'] = eachProject['id']
        if eachProject['errorMessage'] is not None:
            itemDict['errorMessage'] = eachProject['errorMessage']
        itemDict['connectorId'] = eachProject['connectorId']
        itemDict['createdBy'] = eachProject['createdBy']
        itemDict['createDate'] = eachProject['createDate']
        itemDict['programId'] = eachProject['programId']
        itemDict['projectId'] = eachProject['projectId']
        itemDict['projectKey'] = eachProject['projectKey']
        itemDict['projectName'] = eachProject['projectName']
        if eachProject['lastUpdatedBy'] is not None:
            itemDict['lastUpdatedBy'] = eachProject['lastUpdatedBy']
        if eachProject['lastUpdatedDate'] is not None:
            itemDict['lastUpdatedDate'] = eachProject['lastUpdatedDate']
        # Don't save the self field, since it will be generated during creation
        projectsArr.append(itemDict)
    return projectsArr
    
def GetAllCostCenters():
    """ Get all Cost Center information and return to the caller.

        Returns: All the details for each cost center in a list of objects.
    """
    costCenterArr = []
    print("Collecting all Cost Center info...")
    costCenters = GetFromJiraAlign(True, cfg.instanceurl + "/CostCenters")
    dataCostCenter = costCenters.json()
    for eachCostCenter in dataCostCenter:
        itemDict = {}
        itemDict['id'] = eachCostCenter['id']
        if eachCostCenter['description'] is not None:
            itemDict['description'] = eachCostCenter['description']
        itemDict['hourlyRate'] = eachCostCenter['hourlyRate']
        if eachCostCenter['identifier'] is not None:
            itemDict['identifier'] = eachCostCenter['identifier']
        itemDict['name'] = eachCostCenter['name']
        itemDict['ownerId'] = eachCostCenter['ownerId']
        itemDict['regionId'] = eachCostCenter['regionId']
        # Don't save the self field, since it will be generated during creation
        costCenterArr.append(itemDict)
    return costCenterArr

def GetAllDivisions():
    """ Get all Division information and return to the caller.

        Returns: All the details for each division in a list of objects.
    """
    divisionArr = []
    print("Collecting all Division info...")
    divisions = GetFromJiraAlign(True, cfg.instanceurl + "/Divisions")
    dataDivisions = divisions.json()
    for eachDivision in dataDivisions:
        itemDict = {}
        itemDict['id'] = eachDivision['id']
        if eachDivision['companyCode'] is not None:
            itemDict['companyCode'] = eachDivision['companyCode']
        if eachDivision['costCenter'] is not None:
            itemDict['costCenter'] = eachDivision['costCenter']
        if eachDivision['costCenterName'] is not None:
            itemDict['costCenterName'] = eachDivision['costCenterName']
        if eachDivision['createdBy'] is not None:
            itemDict['createdBy'] = eachDivision['createdBy']
        if eachDivision['createDate'] is not None:
            itemDict['createDate'] = eachDivision['createDate']
        itemDict['divisionCategory'] = eachDivision['divisionCategory']
        itemDict['divisionCategoryName'] = eachDivision['divisionCategoryName']
        if eachDivision['parentId'] is not None:
            itemDict['parentId'] = eachDivision['parentId']
        if eachDivision['parentName'] is not None:
            itemDict['parentName'] = eachDivision['parentName']
        if eachDivision['productId'] is not None:
            itemDict['productId'] = eachDivision['productId']
        if eachDivision['productName'] is not None:
            itemDict['productName'] = eachDivision['productName']
        if eachDivision['lastUpdatedBy'] is not None:
            itemDict['lastUpdatedBy'] = eachDivision['lastUpdatedBy']
        if eachDivision['lastUpdatedDate'] is not None:
            itemDict['lastUpdatedDate'] = eachDivision['lastUpdatedDate']
        # Don't save the self field, since it will be generated during creation
        divisionArr.append(itemDict)
    return divisionArr

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

def GetAllRisks():
    """ Get all Risks information and return to the caller.

        Returns: All the details for each risk in a list of objects.
    """
    riskArr = []
    print("Collecting all Risk info...")
    risks = GetFromJiraAlign(True, cfg.instanceurl + "/Risks")
    dataRisks = risks.json()
    for eachRisk in dataRisks:
        itemDict = {}
        itemDict['id'] = eachRisk['id']
        if eachRisk['closeDate'] is not None:
            itemDict['closeDate'] = eachRisk['closeDate']
        if eachRisk['closedBy'] is not None:
            itemDict['closedBy'] = eachRisk['closedBy']
        if eachRisk['consequence'] is not None:
            itemDict['consequence'] = eachRisk['consequence']
        if eachRisk['contingency'] is not None:
            itemDict['contingency'] = eachRisk['contingency']
        itemDict['createdBy'] = eachRisk['createdBy']
        itemDict['createDate'] = eachRisk['createDate']
        if eachRisk['criticalPath'] is not None:
            itemDict['criticalPath'] = eachRisk['criticalPath']
        if eachRisk['customFields'] is not None:
            itemDict['customFields'] = eachRisk['customFields']
        if eachRisk['description'] is not None:
            itemDict['description'] = eachRisk['description']
        if eachRisk['externalId'] is not None:
            itemDict['externalId'] = eachRisk['externalId']
        if eachRisk['externalKey'] is not None:
            itemDict['externalKey'] = eachRisk['externalKey']
        if eachRisk['exposure'] is not None:
            itemDict['exposure'] = eachRisk['exposure']
        if eachRisk['impact'] is not None:
            itemDict['impact'] = eachRisk['impact']
        if eachRisk['mitigation'] is not None:
            itemDict['mitigation'] = eachRisk['mitigation']
        if eachRisk['notify'] is not None:
            itemDict['notify'] = eachRisk['notify']
        if eachRisk['notifySendEmailDate'] is not None:
            itemDict['notifySendEmailDate'] = eachRisk['notifySendEmailDate']
        if eachRisk['occurrence'] is not None:
            itemDict['occurrence'] = eachRisk['occurrence']
        if eachRisk['ownerId'] is not None:
            itemDict['ownerId'] = eachRisk['ownerId']
        if eachRisk['relationship'] is not None:
            itemDict['relationship'] = eachRisk['relationship']
        itemDict['relatedItemId'] = eachRisk['relatedItemId']
        if eachRisk['releaseId'] is not None:
            itemDict['releaseId'] = eachRisk['releaseId']
        if eachRisk['rank'] is not None:
            itemDict['rank'] = eachRisk['rank']
        itemDict['resolutionMethod'] = eachRisk['resolutionMethod']
        if eachRisk['resolutionStatus'] is not None:
            itemDict['resolutionStatus'] = eachRisk['resolutionStatus']
        itemDict['riskType'] = eachRisk['riskType']
        itemDict['status'] = eachRisk['status']
        if eachRisk['tags'] is not None:
            itemDict['tags'] = eachRisk['tags']
        if eachRisk['targetResolutionDate'] is not None:
            itemDict['targetResolutionDate'] = eachRisk['targetResolutionDate']
        itemDict['title'] = eachRisk['title']
        if eachRisk['lastUpdatedBy'] is not None:
            itemDict['lastUpdatedBy'] = eachRisk['lastUpdatedBy']
        if eachRisk['lastUpdatedDate'] is not None:
            itemDict['lastUpdatedDate'] = eachRisk['lastUpdatedDate']
        # Don't save the self field, since it will be generated during creation
        riskArr.append(itemDict)
    return riskArr

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
        if eachUser['holidayCityId'] is not None:
            itemDict['holidayCityId'] = eachUser['holidayCityId']
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
        if eachUser['lastLoginDate'] is not None:
            itemDict['lastLoginDate'] = eachUser['lastLoginDate']
        if eachUser['userType'] is not None:
            itemDict['userType'] = eachUser['userType']
        if eachUser['enterpriseHierarchyId'] is not None:
            itemDict['enterpriseHierarchyId'] = eachUser['enterpriseHierarchyId']
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
        if eachTheme['customFields'] is not None:
            itemDict['customFields'] = eachTheme['customFields']
        if eachTheme['lastUpdatedDate'] is not None:
            itemDict['lastUpdatedDate'] = eachTheme['lastUpdatedDate']
        if cfg.jaVersion.find("10.107") != -1 or cfg.jaVersion.find("10.106") != -1:
            if eachTheme['developmentalStepId'] is not None:
                eachTheme['developmentalStepId'] = eachTheme['developmentalStepId']
            if eachTheme['operationalStepId'] is not None:
                itemDict['operationalStepId'] = eachTheme['operationalStepId']
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
        if cfg.jaVersion.find("10.109") > -1:
            if eachTheme['processStepId'] is not None:
                itemDict['processStepId'] = eachTheme['processStepId']
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

def GetAllCustomers():
    """ Get all Customers information and return to the caller.

        Returns: All the details for each customer in a list of objects.
    """
    customerArr = []
    print("Collecting all Customer info...")
    customers = GetFromJiraAlign(True, cfg.instanceurl + "/customers")
    dataCustomer = customers.json()
    for eachCustomer in dataCustomer:
        itemDict = {}
        itemDict['id'] = eachCustomer['id']
        itemDict['name'] = eachCustomer['name']
        if eachCustomer['lastUpdatedDate'] is not None:
            itemDict['lastUpdatedDate'] = eachCustomer['lastUpdatedDate']
        # Don't save the self field, since it will be generated during creation
        customerArr.append(itemDict)
    return customerArr

def GetAllPortfolios():
    """ Get all Portfolio information and return to the caller.

        Returns: All the details for each portfolio in a list of objects.
    """
    portfolioArr = []
    print("Collecting all Portfolio info...")
    portfolios = GetFromJiraAlign(True, cfg.instanceurl + "/portfolios")
    dataPortfolio = portfolios.json()
    for eachPortfolio in dataPortfolio:
        itemDict = {}
        itemDict['id'] = eachPortfolio['id']
        itemDict['title'] = eachPortfolio['title']
        itemDict['divisionId'] = eachPortfolio['divisionId']
        itemDict['scoreCardId'] = eachPortfolio['scoreCardId']
        itemDict['teamId'] = eachPortfolio['teamId']
        itemDict['isActive'] = eachPortfolio['isActive']
        itemDict['intakeFormId'] = eachPortfolio['intakeFormId']
        itemDict['regionId'] = eachPortfolio['regionId']
        if eachPortfolio['description'] is not None:
            itemDict['description'] = eachPortfolio['description']
        if eachPortfolio['isPrivate'] is not None:
            itemDict['isPrivate'] = eachPortfolio['isPrivate']
        if eachPortfolio['caseDevelopmentId'] is not None:
            itemDict['caseDevelopmentId'] = eachPortfolio['caseDevelopmentId']
        if eachPortfolio['teamDescription'] is not None:
            itemDict['teamDescription'] = eachPortfolio['teamDescription']
        if eachPortfolio['lastUpdatedDate'] is not None:
            itemDict['lastUpdatedDate'] = eachPortfolio['lastUpdatedDate']
        # Don't save the self field, since it will be generated during creation
        portfolioArr.append(itemDict)
    return portfolioArr

def GetAllIdeas():
    """ Get all Ideas information and return to the caller.

        Returns: All the details for each idea in a list of objects.
    """
    ideaArr = []
    print("Collecting all Idea info...")
    ideas = GetFromJiraAlign(True, cfg.instanceurl + "/ideas")
    dataIdeas = ideas.json()
    for eachIdea in dataIdeas:
        itemDict = {}
        itemDict['id'] = eachIdea['id']
        itemDict['groupId'] = eachIdea['groupId']
        itemDict['title'] = eachIdea['title']
        itemDict['createdBy'] = eachIdea['createdBy']
        itemDict['createDate'] = eachIdea['createDate']
        itemDict['ownerId'] = eachIdea['ownerId']
        itemDict['status'] = eachIdea['status']
        itemDict['isExternal'] = eachIdea['isExternal']
        itemDict['companyId'] = eachIdea['companyId']
        itemDict['categoryId'] = eachIdea['categoryId']
        itemDict['isPublic'] = eachIdea['isPublic']
        if eachIdea['productId'] is not None:
            itemDict['productId'] = eachIdea['productId']
        if eachIdea['description'] is not None:
            itemDict['description'] = eachIdea['description']
        # Don't save the self field, since it will be generated during creation
        ideaArr.append(itemDict)
    return ideaArr

def GetAllKeyResults():
    """ Get all Key Results information and return to the caller.

        Returns: All the details for each Key Result in a list of objects.
    """
    keyResultArr = []
    print("Collecting all Key Results info...")
    keyResults = GetFromJiraAlign(True, cfg.instanceurl + "/keyresults")
    dataKeyResults = keyResults.json()
    for eachKeyResult in dataKeyResults:
        itemDict = {}
        itemDict['id'] = eachKeyResult['id']
        itemDict['parentId'] = eachKeyResult['parentId']
        itemDict['parentType'] = eachKeyResult['parentType']
        itemDict['baselineValue'] = eachKeyResult['baselineValue']
        itemDict['targetValue'] = eachKeyResult['targetValue']
        itemDict['type'] = eachKeyResult['type']
        itemDict['weight'] = eachKeyResult['weight']
        itemDict['createDate'] = eachKeyResult['createDate']
        itemDict['ownerId'] = eachKeyResult['ownerId']
        itemDict['score'] = eachKeyResult['score']
        if eachKeyResult['targetDate'] is not None:
            itemDict['targetDate'] = eachKeyResult['targetDate']
        if eachKeyResult['description'] is not None:
            itemDict['description'] = eachKeyResult['description']
        if eachKeyResult['isScoreOveridden'] is not None:
            itemDict['isScoreOveridden'] = eachKeyResult['isScoreOveridden']
        if eachKeyResult['scoreOverrides'] is not None:
            itemDict['scoreOverrides'] = eachKeyResult['scoreOverrides']
        if eachKeyResult['valueUpdates'] is not None:
            itemDict['valueUpdates'] = eachKeyResult['valueUpdates']
        if eachKeyResult['lastUpdatedDate'] is not None:
            itemDict['lastUpdatedDate'] = eachKeyResult['lastUpdatedDate']
        # Don't save the self field, since it will be generated during creation
        keyResultArr.append(itemDict)
    return keyResultArr

def GetAllMilestones():
    """ Get all Milestones information and return to the caller.

        Returns: All the details for each Milestone in a list of objects.
    """
    milestoneArr = []
    print("Collecting all Milestone info...")
    milestones = GetFromJiraAlign(True, cfg.instanceurl + "/milestones")
    dataMilestones = milestones.json()
    for eachMilestone in dataMilestones:
        itemDict = {}
        itemDict['id'] = eachMilestone['id']
        itemDict['tier'] = eachMilestone['tier']
        itemDict['programId'] = eachMilestone['programId']
        itemDict['type'] = eachMilestone['type']
        itemDict['isBlocked'] = eachMilestone['isBlocked']
        itemDict['ownerId'] = eachMilestone['ownerId']
        itemDict['name'] = eachMilestone['name']
        itemDict['createDate'] = eachMilestone['createDate']
        if eachMilestone['description'] is not None:
            itemDict['description'] = eachMilestone['description']
        if eachMilestone['status'] is not None:
            itemDict['status'] = eachMilestone['status']
        if eachMilestone['notes'] is not None:
            itemDict['notes'] = eachMilestone['notes']
        if eachMilestone['startInitiationDate'] is not None:
            itemDict['startInitiationDate'] = eachMilestone['startInitiationDate']
        if eachMilestone['endDate'] is not None:
            itemDict['endDate'] = eachMilestone['endDate']
        if eachMilestone['category'] is not None:
            itemDict['category'] = eachMilestone['category']
        if eachMilestone['targetSyncSprintId'] is not None:
            itemDict['targetSyncSprintId'] = eachMilestone['targetSyncSprintId']
        if eachMilestone['plannedValue'] is not None:
            itemDict['plannedValue'] = eachMilestone['plannedValue']
        if eachMilestone['themeId'] is not None:
            itemDict['themeId'] = eachMilestone['themeId']
        if eachMilestone['deliveredValue'] is not None:
            itemDict['deliveredValue'] = eachMilestone['deliveredValue']
        if eachMilestone['blockedReason'] is not None:
            itemDict['blockedReason'] = eachMilestone['blockedReason']
        if eachMilestone['targetCompletionDate'] is not None:
            itemDict['targetCompletionDate'] = eachMilestone['targetCompletionDate']
        if eachMilestone['portfolioAskDate'] is not None:
            itemDict['portfolioAskDate'] = eachMilestone['portfolioAskDate']
        if eachMilestone['health'] is not None:
            itemDict['health'] = eachMilestone['health']
        if eachMilestone['parentId'] is not None:
            itemDict['parentId'] = eachMilestone['parentId']
        if eachMilestone['score'] is not None:
            itemDict['score'] = eachMilestone['score']
        if eachMilestone['portfolioId'] is not None:
            itemDict['portfolioId'] = eachMilestone['portfolioId']
        if eachMilestone['goalId'] is not None:
            itemDict['goalId'] = eachMilestone['goalId']
        if eachMilestone['solutionId'] is not None:
            itemDict['solutionId'] = eachMilestone['solutionId']
        if eachMilestone['notificationStartDate'] is not None:
            itemDict['notificationStartDate'] = eachMilestone['notificationStartDate']
        if eachMilestone['notificationFrequency'] is not None:
            itemDict['notificationFrequency'] = eachMilestone['notificationFrequency']
        if eachMilestone['reference'] is not None:
            itemDict['reference'] = eachMilestone['reference']
        if eachMilestone['programIds'] is not None:
            itemDict['programIds'] = eachMilestone['programIds']
        if eachMilestone['releaseIds'] is not None:
            itemDict['releaseIds'] = eachMilestone['releaseIds']
        if eachMilestone['featureIds'] is not None:
            itemDict['featureIds'] = eachMilestone['featureIds']
        if eachMilestone['impedimentIds'] is not None:
            itemDict['impedimentIds'] = eachMilestone['impedimentIds']
        if eachMilestone['riskIds'] is not None:
            itemDict['riskIds'] = eachMilestone['riskIds']
        if eachMilestone['dependencyIds'] is not None:
            itemDict['dependencyIds'] = eachMilestone['dependencyIds']
        if eachMilestone['customFields'] is not None:
            itemDict['customFields'] = eachMilestone['customFields']
        if eachMilestone['teamIds'] is not None:
            itemDict['teamIds'] = eachMilestone['teamIds']
        if eachMilestone['lastUpdatedBy'] is not None:
            itemDict['lastUpdatedBy'] = eachMilestone['lastUpdatedBy']
        if eachMilestone['lastUpdatedDate'] is not None:
            itemDict['lastUpdatedDate'] = eachMilestone['lastUpdatedDate']
        # Don't save the self field, since it will be generated during creation
        milestoneArr.append(itemDict)
    return milestoneArr

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
        itemDict['releaseNumber'] = eachRelease['releaseNumber']
        itemDict['scheduleType'] = eachRelease['scheduleType']
        itemDict['roadmap'] = eachRelease['roadmap']
        itemDict['budget'] = eachRelease['budget']
        itemDict['health'] = eachRelease['health']
        if eachRelease['createDate'] is not None:
            itemDict['createDate'] = eachRelease['createDate']
        if eachRelease['startDate'] is not None:
            itemDict['startDate'] = eachRelease['startDate']
        if eachRelease['endDate'] is not None:
            itemDict['endDate'] = eachRelease['endDate']
        if eachRelease['testSuite'] is not None:
            itemDict['testSuite'] = eachRelease['testSuite']
        if eachRelease['portfolioId'] is not None:
            itemDict['portfolioId'] = eachRelease['portfolioId']
        if eachRelease['predecessorId'] is not None:
            itemDict['predecessorId'] = eachRelease['predecessorId']
        if eachRelease['score1'] is not None:
            itemDict['score1'] = eachRelease['score1']
        if eachRelease['score2'] is not None:
            itemDict['score2'] = eachRelease['score2']
        if eachRelease['score3'] is not None:
            itemDict['score3'] = eachRelease['score3']
        if eachRelease['score4'] is not None:
            itemDict['score4'] = eachRelease['score4']
        if eachRelease['blendedHourlyRate'] is not None:
            itemDict['blendedHourlyRate'] = eachRelease['blendedHourlyRate']
        if eachRelease['divisionId'] is not None:
            itemDict['divisionId'] = eachRelease['divisionId']
        if eachRelease['programIds'] is not None:
            itemDict['programIds'] = eachRelease['programIds']
        if ('regionIds' in eachRelease) and (eachRelease['regionIds'] is not None):
            itemDict['regionIds'] = eachRelease['regionIds']
        if ('anchorSprintIds' in eachRelease) and (eachRelease['anchorSprintIds'] is not None):
            itemDict['anchorSprintIds'] = eachRelease['anchorSprintIds']
        if eachRelease['lastUpdatedBy'] is not None:
            itemDict['lastUpdatedBy'] = eachRelease['lastUpdatedBy']
        if eachRelease['lastUpdatedDate'] is not None:
            itemDict['lastUpdatedDate'] = eachRelease['lastUpdatedDate']
        if eachRelease['releaseNumber'] is not None:
            itemDict['releaseNumber'] = eachRelease['releaseNumber']
        # Don't save the self field, since it will be generated during creation
        releaseArr.append(itemDict)
    return releaseArr

def GetAllReleaseVehicles():
    """ Get all Release Vehicles information and return to the caller.

        Returns: All the details for each release vehicle in a list of objects.
    """
    releaseVehicleArr = []
    print("Collecting all Release Vehicles info...")
    releaseVehicles = GetFromJiraAlign(True, cfg.instanceurl + "/releasevehicles")
    dataReleaseVehicle = releaseVehicles.json()
    for eachReleaseVehicle in dataReleaseVehicle:
        itemDict = {}
        itemDict['id'] = eachReleaseVehicle['id']
        itemDict['name'] = eachReleaseVehicle['name']
        itemDict['releaseId'] = eachReleaseVehicle['releaseId']
        itemDict['storiesCount'] = eachReleaseVehicle['storiesCount']
        itemDict['storyIds'] = eachReleaseVehicle['storyIds']
        itemDict['storiesPercentComplete'] = eachReleaseVehicle['storiesPercentComplete']
        itemDict['contributingTeamsCount'] = eachReleaseVehicle['contributingTeamsCount']
        itemDict['contributingProgramsCount'] = eachReleaseVehicle['contributingProgramsCount']
        if eachReleaseVehicle['releaseName'] is not None:
            itemDict['releaseName'] = eachReleaseVehicle['releaseName']
        if eachReleaseVehicle['shipDate'] is not None:
            itemDict['shipDate'] = eachReleaseVehicle['shipDate']
        if eachReleaseVehicle['startDate'] is not None:
            itemDict['startDate'] = eachReleaseVehicle['startDate']
        if eachReleaseVehicle['health'] is not None:
            itemDict['health'] = eachReleaseVehicle['health']
        if eachReleaseVehicle['externalId'] is not None:
            itemDict['externalId'] = eachReleaseVehicle['externalId']
        if eachReleaseVehicle['goLiveDate'] is not None:
            itemDict['goLiveDate'] = eachReleaseVehicle['goLiveDate']
        if eachReleaseVehicle['connectorId'] is not None:
            itemDict['connectorId'] = eachReleaseVehicle['connectorId']
        if eachReleaseVehicle['ownerId'] is not None:
            itemDict['ownerId'] = eachReleaseVehicle['ownerId']
        if eachReleaseVehicle['jiraProjectKey'] is not None:
            itemDict['jiraProjectKey'] = eachReleaseVehicle['jiraProjectKey']
        if eachReleaseVehicle['status'] is not None:
            itemDict['status'] = eachReleaseVehicle['status']
        if eachReleaseVehicle['closedDate'] is not None:
            itemDict['closedDate'] = eachReleaseVehicle['closedDate']
        if eachReleaseVehicle['type'] is not None:
            itemDict['type'] = eachReleaseVehicle['type']
        if eachReleaseVehicle['createDate'] is not None:
            itemDict['createDate'] = eachReleaseVehicle['createDate']
        if eachReleaseVehicle['externalProjectId'] is not None:
            itemDict['externalProjectId'] = eachReleaseVehicle['externalProjectId']
        if eachReleaseVehicle['isTimeTrackingOnly'] is not None:
            itemDict['isTimeTrackingOnly'] = eachReleaseVehicle['isTimeTrackingOnly']
        if eachReleaseVehicle['teamIds'] is not None:
            itemDict['teamIds'] = eachReleaseVehicle['teamIds']
        if eachReleaseVehicle['portfolioIds'] is not None:
            itemDict['portfolioIds'] = eachReleaseVehicle['portfolioIds']
        if eachReleaseVehicle['programIds'] is not None:
            itemDict['programIds'] = eachReleaseVehicle['programIds']
        if eachReleaseVehicle['lastUpdatedDate'] is not None:
            itemDict['lastUpdatedDate'] = eachReleaseVehicle['lastUpdatedDate']
        # Don't save the self field, since it will be generated during creation
        releaseVehicleArr.append(itemDict)
    return releaseVehicleArr

def GetAllTeams():
    """ Get all Teams information and return to the caller.

        Returns: All the details for each team in a list of objects.
    """
    teamsArr = []
    print("Collecting all Teams info...")

    # Teams are only supported for JA Version 10.108 or later
    if cfg.jaVersion.find("10.108") != -1 and cfg.jaVersion.find("10.109") != -1\
        and cfg.jaVersion.find("10.110") != -1:
        return teamsArr

    teams = GetFromJiraAlign(True, cfg.instanceurl + "/Teams")
    dataTeams = teams.json()
    for eachTeam in dataTeams:
        itemDict = {}
        itemDict['id'] = eachTeam['id']
        itemDict['name'] = eachTeam['name']
        itemDict['ownerId'] = eachTeam['ownerId']
        itemDict['type'] = eachTeam['type']
        itemDict['isActive'] = eachTeam['isActive']
        if eachTeam['regionId'] is not None:
            itemDict['regionId'] = eachTeam['regionId']
        if eachTeam['programId'] is not None:
            itemDict['programId'] = eachTeam['programId']
        if eachTeam['programIds'] is not None:
            itemDict['programIds'] = eachTeam['programIds']
        if eachTeam['description'] is not None:
            itemDict['description'] = eachTeam['description']
        if eachTeam['sprintPrefix'] is not None:
            itemDict['sprintPrefix'] = eachTeam['sprintPrefix']
        if eachTeam['shortName'] is not None:
            itemDict['shortName'] = eachTeam['shortName']
        if eachTeam['trackBy'] is not None:
            itemDict['trackBy'] = eachTeam['trackBy']
        if eachTeam['maxAllocation'] is not None:
            itemDict['maxAllocation'] = eachTeam['maxAllocation']
        if eachTeam['allowTaskDeletion'] is not None:
            itemDict['allowTaskDeletion'] = eachTeam['allowTaskDeletion']
        if eachTeam['allowTeamToRunStandup'] is not None:
            itemDict['allowTeamToRunStandup'] = eachTeam['allowTeamToRunStandup']
        if eachTeam['isKanbanTeam'] is not None:
            itemDict['isKanbanTeam'] = eachTeam['isKanbanTeam']
        if eachTeam['createDate'] is not None:
            itemDict['createDate'] = eachTeam['createDate']
        if eachTeam['lastUpdatedDate'] is not None:
            itemDict['lastUpdatedDate'] = eachTeam['lastUpdatedDate']
        if eachTeam['enableAutoEstimate'] is not None:
            itemDict['enableAutoEstimate'] = eachTeam['enableAutoEstimate']
        if eachTeam['autoEstimateValue'] is not None:
            itemDict['autoEstimateValue'] = eachTeam['autoEstimateValue']
        if eachTeam['throughput'] is not None:
            itemDict['throughput'] = eachTeam['throughput']
        if eachTeam['communityIds'] is not None:
            itemDict['communityIds'] = eachTeam['communityIds']
        # Don't save the self field, since it will be generated during creation
        teamsArr.append(itemDict)
    return teamsArr

def GetAllValueStreams():
    """ Get all Value Stream information and return to the caller.

        Returns: All the details for each value stream in a list of objects.
    """
    valueStreamArr = []
    print("Collecting all Value Stream info...")

    # Value Streams are only supported for JA Version 10.108 or later
    if cfg.jaVersion.find("10.108") != -1 and cfg.jaVersion.find("10.109") != -1\
        and cfg.jaVersion.find("10.110") != -1:
        return valueStreamArr

    valueStreams = GetFromJiraAlign(True, cfg.instanceurl + "/ValueStreams")
    dataValueStreams = valueStreams.json()
    for eachValueStream in dataValueStreams:
        itemDict = {}
        itemDict['id'] = eachValueStream['id']
        itemDict['name'] = eachValueStream['name']
        itemDict['level'] = eachValueStream['level']
        itemDict['teamId'] = eachValueStream['teamId']
        itemDict['isActive'] = eachValueStream['isActive']
        itemDict['mapToState'] = eachValueStream['mapToState']
        if eachValueStream['teamDescription'] is not None:
            itemDict['teamDescription'] = eachValueStream['teamDescription']
        if eachValueStream['regionId'] is not None:
            itemDict['regionId'] = eachValueStream['regionId']

        if eachValueStream['programIds'] is not None:
            itemDict['programIds'] = eachValueStream['programIds']
        if eachValueStream['customerIds'] is not None:
            itemDict['customerIds'] = eachValueStream['customerIds']
        if eachValueStream['processSteps'] is not None:
            itemDict['processSteps'] = eachValueStream['processSteps']
        if eachValueStream['createdBy'] is not None:
            itemDict['createdBy'] = eachValueStream['createdBy']
        if eachValueStream['createDate'] is not None:
            itemDict['createDate'] = eachValueStream['createDate']
        if eachValueStream['lastUpdatedDate'] is not None:
            itemDict['lastUpdatedDate'] = eachValueStream['lastUpdatedDate']
        if eachValueStream['lastUpdatedBy'] is not None:
            itemDict['lastUpdatedBy'] = eachValueStream['lastUpdatedBy']
        # Don't save the self field, since it will be generated during creation
        valueStreamArr.append(itemDict)
    return valueStreamArr

def ExtractItemData(itemType, sourceItem, extractedData):
    """ Extract all applicable fields from the source item and add them to the extracted
        data, based on item type.
        Generic version, checks for a key's existance in the source before attempting to copy
        it over -- easier to maintain.

    Args:
        itemType: Which type of work the sourceItem is: epics, features, stories, defects, tasks, programs
        sourceItem: Full set of data for this item from Jira Align
        extractedData: All the data that needs to be saved from this sourceItem
    """
    # These will always exist
    extractedData['id'] = sourceItem['id']
    extractedData['itemtype'] = itemType
    
    # Check to see if each key exists in sourceItem, and if it does, then check to
    # see if the value is NOT None.  If it's not None, then copy the data over.
    if ('abilityToExec' in sourceItem) and (sourceItem['abilityToExec'] is not None):
        extractedData['abilityToExec'] = sourceItem['abilityToExec']
    if ('acceptedDate' in sourceItem) and (sourceItem['acceptedDate'] is not None):
        extractedData['acceptedDate'] = sourceItem['acceptedDate']
    if ('acceptedUserId' in sourceItem) and (sourceItem['acceptedUserId'] is not None):
        extractedData['acceptedUserId'] = sourceItem['acceptedUserId']
    if ('actualEndDate' in sourceItem) and (sourceItem['actualEndDate'] is not None):
        extractedData['actualEndDate'] = sourceItem['actualEndDate']
    if ('additionalProgramIds' in sourceItem) and (sourceItem['additionalProgramIds'] is not None):
        extractedData['additionalProgramIds'] = sourceItem['additionalProgramIds']
    if ('additionalProcessStepIds' in sourceItem) and (sourceItem['additionalProcessStepIds'] is not None):
        extractedData['additionalProcessStepIds'] = sourceItem['additionalProcessStepIds']
    if ('affectedCountryIds' in sourceItem) and (sourceItem['affectedCountryIds'] is not None):
        extractedData['affectedCountryIds'] = sourceItem['affectedCountryIds']
    if ('allowTaskDeletion' in sourceItem) and (sourceItem['allowTaskDeletion'] is not None):
        extractedData['allowTaskDeletion'] = sourceItem['allowTaskDeletion']
    if ('allowTeamToRunStandup' in sourceItem) and (sourceItem['allowTeamToRunStandup'] is not None):
        extractedData['allowTeamToRunStandup'] = sourceItem['allowTeamToRunStandup']
    if ('anchorSprint' in sourceItem) and (sourceItem['anchorSprint'] is not None):
        extractedData['anchorSprint'] = sourceItem['anchorSprint']
    if ('anchorSprintId' in sourceItem) and (sourceItem['anchorSprintId'] is not None):
        extractedData['anchorSprintId'] = sourceItem['anchorSprintId']
    if ('anchorSprintIds' in sourceItem) and (sourceItem['anchorSprintIds'] is not None):
        extractedData['anchorSprintIds'] = sourceItem['anchorSprintIds']
    if ('associatedTicket' in sourceItem) and (sourceItem['associatedTicket'] is not None):
        extractedData['associatedTicket'] = sourceItem['associatedTicket']
    if ('autoEstimateValue' in sourceItem) and (sourceItem['autoEstimateValue'] is not None):
        extractedData['autoEstimateValue'] = sourceItem['autoEstimateValue']
    if ('beginDate' in sourceItem) and (sourceItem['beginDate'] is not None):
        extractedData['beginDate'] = sourceItem['beginDate']
    if ('benefits' in sourceItem) and (sourceItem['benefits'] is not None):
        extractedData['benefits'] = sourceItem['benefits']
    if ('blendedHourlyRate' in sourceItem) and (sourceItem['blendedHourlyRate'] is not None):
        extractedData['blendedHourlyRate'] = sourceItem['blendedHourlyRate']
    if ('blockedReason' in sourceItem) and (sourceItem['blockedReason'] is not None):
        extractedData['blockedReason'] = sourceItem['blockedReason']
    if ('budget' in sourceItem) and (sourceItem['budget'] is not None):
        extractedData['budget'] = sourceItem['budget']
    if ('businessDriver' in sourceItem) and (sourceItem['businessDriver'] is not None):
        extractedData['businessDriver'] = sourceItem['businessDriver']
    if ('businessImpact' in sourceItem) and (sourceItem['businessImpact'] is not None):
        extractedData['businessImpact'] = sourceItem['businessImpact']
    if ('businessValue' in sourceItem) and (sourceItem['businessValue'] is not None):
        extractedData['businessValue'] = sourceItem['businessValue']
    if ('capitalized' in sourceItem) and (sourceItem['capitalized'] is not None):
        extractedData['capitalized'] = sourceItem['capitalized']
    if ('caseDevelopmentId' in sourceItem) and (sourceItem['caseDevelopmentId'] is not None):
        extractedData['caseDevelopmentId'] = sourceItem['caseDevelopmentId']
    if ('category' in sourceItem) and (sourceItem['category'] is not None):
        extractedData['category'] = sourceItem['category']
    if ('city' in sourceItem) and (sourceItem['city'] is not None):
        extractedData['city'] = sourceItem['city']
    if ('cityId' in sourceItem) and (sourceItem['cityId'] is not None):
        extractedData['cityId'] = sourceItem['cityId']
    if ('closeDate' in sourceItem) and (sourceItem['closeDate'] is not None):
        extractedData['closeDate'] = sourceItem['closeDate']
    if ('color' in sourceItem) and (sourceItem['color'] is not None):
        extractedData['color'] = sourceItem['color']
    if ('communityIds' in sourceItem) and (sourceItem['communityIds'] is not None):
        extractedData['communityIds'] = sourceItem['communityIds']
    if ('company' in sourceItem) and (sourceItem['company'] is not None):
        extractedData['company'] = sourceItem['company']
    if ('companyId' in sourceItem) and (sourceItem['companyId'] is not None):
        extractedData['companyId'] = sourceItem['companyId']
    if ('completedDate' in sourceItem) and (sourceItem['completedDate'] is not None):
        extractedData['completedDate'] = sourceItem['completedDate']
    if ('complexity' in sourceItem) and (sourceItem['complexity'] is not None):
        extractedData['complexity'] = sourceItem['complexity']
    if ('connectorId' in sourceItem) and (sourceItem['connectorId'] is not None):
        extractedData['connectorId'] = sourceItem['connectorId']
    if ('costCenter' in sourceItem) and (sourceItem['costCenter'] is not None):
        extractedData['costCenter'] = sourceItem['costCenter']
    if ('costCenterId' in sourceItem) and (sourceItem['costCenterId'] is not None):
        extractedData['costCenterId'] = sourceItem['costCenterId']
    if ('createDate' in sourceItem) and (sourceItem['createDate'] is not None):
        extractedData['createDate'] = sourceItem['createDate']
    if ('createdBy' in sourceItem) and (sourceItem['createdBy'] is not None):
        extractedData['createdBy'] = sourceItem['createdBy']
    if ('customerIds' in sourceItem) and (sourceItem['customerIds'] is not None):
        extractedData['customerIds'] = sourceItem['customerIds']
    if ('customFields' in sourceItem) and (sourceItem['customFields'] is not None):
        extractedData['customFields'] = sourceItem['customFields']
    if ('defectAllocation' in sourceItem) and (sourceItem['defectAllocation'] is not None):
        extractedData['defectAllocation'] = sourceItem['defectAllocation']
    if ('deliveredValue' in sourceItem) and (sourceItem['deliveredValue'] is not None):
        extractedData['deliveredValue'] = sourceItem['deliveredValue']
    if ('dependencyIds' in sourceItem) and (sourceItem['dependencyIds'] is not None):
        extractedData['dependencyIds'] = sourceItem['dependencyIds']
    if ('description' in sourceItem) and (sourceItem['description'] is not None):
        extractedData['description'] = sourceItem['description']
    if ('descriptionRich' in sourceItem) and (sourceItem['descriptionRich'] is not None):
        extractedData['descriptionRich'] = sourceItem['descriptionRich']
    if ('dependencyIds' in sourceItem) and (sourceItem['dependencyIds'] is not None):
        extractedData['dependencyIds'] = sourceItem['dependencyIds']
    if ('designStage' in sourceItem) and (sourceItem['designStage'] is not None):
        extractedData['designStage'] = sourceItem['designStage']
    if ('devCompleteBy' in sourceItem) and (sourceItem['devCompleteBy'] is not None):
        extractedData['devCompleteBy'] = sourceItem['devCompleteBy']
    if ('devCompleteDate' in sourceItem) and (sourceItem['devCompleteDate'] is not None):
        extractedData['devCompleteDate'] = sourceItem['devCompleteDate']
    if ('discountRate' in sourceItem) and (sourceItem['discountRate'] is not None):
        extractedData['discountRate'] = sourceItem['discountRate']
    if ('division' in sourceItem) and (sourceItem['division'] is not None):
        extractedData['division'] = sourceItem['division']
    if ('divisionId' in sourceItem) and (sourceItem['divisionId'] is not None):
        extractedData['divisionId'] = sourceItem['divisionId']
    if ('efficiencyDividend' in sourceItem) and (sourceItem['efficiencyDividend'] is not None):
        extractedData['efficiencyDividend'] = sourceItem['efficiencyDividend']
    if ('effortHours' in sourceItem) and (sourceItem['effortHours'] is not None):
        extractedData['effortHours'] = sourceItem['effortHours']
    if ('effortPoints' in sourceItem) and (sourceItem['effortPoints'] is not None):
        extractedData['effortPoints'] = sourceItem['effortPoints']
    if ('effortSwag' in sourceItem) and (sourceItem['effortSwag'] is not None):
        extractedData['effortSwag'] = sourceItem['effortSwag']
    if ('email' in sourceItem) and (sourceItem['email'] is not None):
        extractedData['email'] = sourceItem['email']
    if ('employeeClassification' in sourceItem) and (sourceItem['employeeClassification'] is not None):
        extractedData['employeeClassification'] = sourceItem['employeeClassification']
    if ('employeeId' in sourceItem) and (sourceItem['employeeId'] is not None):
        extractedData['employeeId'] = sourceItem['employeeId']
    if ('enableAutoEstimate' in sourceItem) and (sourceItem['enableAutoEstimate'] is not None):
        extractedData['enableAutoEstimate'] = sourceItem['enableAutoEstimate']
    if ('endDate' in sourceItem) and (sourceItem['endDate'] is not None):
        extractedData['endDate'] = sourceItem['endDate']
    if ('endSprintId' in sourceItem) and (sourceItem['endSprintId'] is not None):
        extractedData['endSprintId'] = sourceItem['endSprintId']
    if ('enterpriseHierarchy' in sourceItem) and (sourceItem['enterpriseHierarchy'] is not None):
        extractedData['enterpriseHierarchy'] = sourceItem['enterpriseHierarchy']
    if ('enterpriseHierarchyId' in sourceItem) and (sourceItem['enterpriseHierarchyId'] is not None):
        extractedData['enterpriseHierarchyId'] = sourceItem['enterpriseHierarchyId']
    if ('epicObjectId' in sourceItem) and (sourceItem['epicObjectId'] is not None):
        extractedData['epicObjectId'] = sourceItem['epicObjectId']
    if ('estimateAtCompletion' in sourceItem) and (sourceItem['estimateAtCompletion'] is not None):
        extractedData['estimateAtCompletion'] = sourceItem['estimateAtCompletion']
    if ('estimateTshirt' in sourceItem) and (sourceItem['estimateTshirt'] is not None):
        extractedData['estimateTshirt'] = sourceItem['estimateTshirt']
    if ('estimationEffortPercent' in sourceItem) and (sourceItem['estimationEffortPercent'] is not None):
        extractedData['estimationEffortPercent'] = sourceItem['estimationEffortPercent']
    if ('expenseSavings' in sourceItem) and (sourceItem['expenseSavings'] is not None):
        extractedData['expenseSavings'] = sourceItem['expenseSavings']
    if ('externalCapEx' in sourceItem) and (sourceItem['externalCapEx'] is not None):
        extractedData['externalCapEx'] = sourceItem['externalCapEx']
    if ('externalId' in sourceItem) and (sourceItem['externalId'] is not None):
        extractedData['externalId'] = sourceItem['externalId']
    if ('externalKey' in sourceItem) and (sourceItem['externalKey'] is not None):
        extractedData['externalKey'] = sourceItem['externalKey']
    if ('externalOpEx' in sourceItem) and (sourceItem['externalOpEx'] is not None):
        extractedData['externalOpEx'] = sourceItem['externalOpEx']
    if ('externalProject' in sourceItem) and (sourceItem['externalProject'] is not None):
        extractedData['externalProject'] = sourceItem['externalProject']
    if ('externalUser' in sourceItem) and (sourceItem['externalUser'] is not None):
        extractedData['externalUser'] = sourceItem['externalUser']
    if ('failureImpact' in sourceItem) and (sourceItem['failureImpact'] is not None):
        extractedData['failureImpact'] = sourceItem['failureImpact']
    if ('failureProbability' in sourceItem) and (sourceItem['failureProbability'] is not None):
        extractedData['failureProbability'] = sourceItem['failureProbability']
    if ('featureId' in sourceItem) and (sourceItem['featureId'] is not None):
        extractedData['featureId'] = sourceItem['featureId']
    if ('featureIds' in sourceItem) and (sourceItem['featureIds'] is not None):
        extractedData['featureIds'] = sourceItem['featureIds']
    if ('featureRank' in sourceItem) and (sourceItem['featureRank'] is not None):
        extractedData['featureRank'] = sourceItem['featureRank']
    if ('featureSummary' in sourceItem) and (sourceItem['featureSummary'] is not None):
        extractedData['featureSummary'] = sourceItem['featureSummary']
    if ('fcastShare' in sourceItem) and (sourceItem['fcastShare'] is not None):
        extractedData['fcastShare'] = sourceItem['fcastShare']
    if ('firstName' in sourceItem) and (sourceItem['firstName'] is not None):
        extractedData['firstName'] = sourceItem['firstName']
    if ('forecastYears' in sourceItem) and (sourceItem['forecastYears'] is not None):
        extractedData['forecastYears'] = sourceItem['forecastYears']
    if ('functionalArea' in sourceItem) and (sourceItem['functionalArea'] is not None):
        extractedData['functionalArea'] = sourceItem['functionalArea']
    if ('fullName' in sourceItem) and (sourceItem['fullName'] is not None):
        extractedData['fullName'] = sourceItem['fullName']
    if ('fundingStage' in sourceItem) and (sourceItem['fundingStage'] is not None):
        extractedData['fundingStage'] = sourceItem['fundingStage']
    if ('goal' in sourceItem) and (sourceItem['goal'] is not None):
        extractedData['goal'] = sourceItem['goal']
    if ('goalId' in sourceItem) and (sourceItem['goalId'] is not None):
        extractedData['goalId'] = sourceItem['goalId']
    if ('health' in sourceItem) and (sourceItem['health'] is not None):
        extractedData['health'] = sourceItem['health']
    if ('holidayCalendar' in sourceItem) and (sourceItem['holidayCalendar'] is not None):
        extractedData['holidayCalendar'] = sourceItem['holidayCalendar']
    if ('holidayCity' in sourceItem) and (sourceItem['holidayCity'] is not None):
        extractedData['holidayCity'] = sourceItem['holidayCity']
    if ('holidayCityId' in sourceItem) and (sourceItem['holidayCityId'] is not None):
        extractedData['holidayCityId'] = sourceItem['holidayCityId']
    if ('holidayRegionId' in sourceItem) and (sourceItem['holidayRegionId'] is not None):
        extractedData['holidayRegionId'] = sourceItem['holidayRegionId']
    if ('hoursEstimate' in sourceItem) and (sourceItem['hoursEstimate'] is not None):
        extractedData['hoursEstimate'] = sourceItem['hoursEstimate']
    if ('hypothesis' in sourceItem) and (sourceItem['hypothesis'] is not None):
        extractedData['hypothesis'] = sourceItem['hypothesis']
    if ('impedimentIds' in sourceItem) and (sourceItem['impedimentIds'] is not None):
        extractedData['impedimentIds'] = sourceItem['impedimentIds']
    if ('includeHours' in sourceItem) and (sourceItem['includeHours'] is not None):
        extractedData['includeHours'] = sourceItem['includeHours']
    if ('initialInvestment' in sourceItem) and (sourceItem['initialInvestment'] is not None):
        extractedData['initialInvestment'] = sourceItem['initialInvestment']
    if ('investmentType' in sourceItem) and (sourceItem['investmentType'] is not None):
        extractedData['investmentType'] = sourceItem['investmentType']
    if ('inProgressBy' in sourceItem) and (sourceItem['inProgressBy'] is not None):
        extractedData['inProgressBy'] = sourceItem['inProgressBy']
    if ('inProgressDate' in sourceItem) and (sourceItem['inProgressDate'] is not None):
        extractedData['inProgressDate'] = sourceItem['inProgressDate']
    if ('inProgressDateEnd' in sourceItem) and (sourceItem['inProgressDateEnd'] is not None):
        extractedData['inProgressDateEnd'] = sourceItem['inProgressDateEnd']
    if ('inScope' in sourceItem) and (sourceItem['inScope'] is not None):
        extractedData['inScope'] = sourceItem['inScope']
    if ('intakeFormId' in sourceItem) and (sourceItem['intakeFormId'] is not None):
        extractedData['intakeFormId'] = sourceItem['intakeFormId']
    if ('isActive' in sourceItem) and (sourceItem['isActive'] is not None):
        extractedData['isActive'] = sourceItem['isActive']
    if ('isBlocked' in sourceItem) and (sourceItem['isBlocked'] is not None):
        extractedData['isBlocked'] = sourceItem['isBlocked']
    if ('isCanceled' in sourceItem) and (sourceItem['isCanceled'] is not None):
        extractedData['isCanceled'] = sourceItem['isCanceled']
    if ('isComplianceManager' in sourceItem) and (sourceItem['isComplianceManager'] is not None):
        extractedData['isComplianceManager'] = sourceItem['isComplianceManager']
    if ('isExternal' in sourceItem) and (sourceItem['isExternal'] is not None):
        extractedData['isExternal'] = sourceItem['isExternal']
    if ('isImport' in sourceItem) and (sourceItem['isImport'] is not None):
        extractedData['isImport'] = sourceItem['isImport']
    if ('isKanbanTeam' in sourceItem) and (sourceItem['isKanbanTeam'] is not None):
        extractedData['isKanbanTeam'] = sourceItem['isKanbanTeam']
    if ('isLocked' in sourceItem) and (sourceItem['isLocked'] is not None):
        extractedData['isLocked'] = sourceItem['isLocked']
    if ('isMultiProgram' in sourceItem) and (sourceItem['isMultiProgram'] is not None):
        extractedData['isMultiProgram'] = sourceItem['isMultiProgram']
    if ('isRecycled' in sourceItem) and (sourceItem['isRecycled'] is not None):
        extractedData['isRecycled'] = sourceItem['isRecycled']
    if ('isSolution' in sourceItem) and (sourceItem['isSolution'] is not None):
        extractedData['isSolution'] = sourceItem['isSolution']
    if ('isSplit' in sourceItem) and (sourceItem['isSplit'] is not None):
        extractedData['isSplit'] = sourceItem['isSplit']
    if ('isTimeTracking' in sourceItem) and (sourceItem['isTimeTracking'] is not None):
        extractedData['isTimeTracking'] = sourceItem['isTimeTracking']
    if ('isUserManager' in sourceItem) and (sourceItem['isUserManager'] is not None):
        extractedData['isUserManager'] = sourceItem['isUserManager']
    if ('itemToSyncDate' in sourceItem) and (sourceItem['itemToSyncDate'] is not None):
        extractedData['itemToSyncDate'] = sourceItem['itemToSyncDate']
    if ('iterationId' in sourceItem) and (sourceItem['iterationId'] is not None):
        extractedData['iterationId'] = sourceItem['iterationId']
    if ('iterationSort' in sourceItem) and (sourceItem['iterationSort'] is not None):
        extractedData['iterationSort'] = sourceItem['iterationSort']
    if ('itemtype' in sourceItem) and (sourceItem['itemtype'] is not None):
        extractedData['itemtype'] = sourceItem['itemtype']
    if ('itrisk' in sourceItem) and (sourceItem['itrisk'] is not None):
        extractedData['itrisk'] = sourceItem['itrisk']
    if ('itRisk' in sourceItem) and (sourceItem['itRisk'] is not None):
        extractedData['itRisk'] = sourceItem['itRisk']
    if ('jiraProjectKey' in sourceItem) and (sourceItem['jiraProjectKey'] is not None):
        extractedData['jiraProjectKey'] = sourceItem['jiraProjectKey']
    if ('lastLoginDate' in sourceItem) and (sourceItem['lastLoginDate'] is not None):
        extractedData['lastLoginDate'] = sourceItem['lastLoginDate']
    if ('lastName' in sourceItem) and (sourceItem['lastName'] is not None):
        extractedData['lastName'] = sourceItem['lastName']
    if ('lastUpdatedBy' in sourceItem) and (sourceItem['lastUpdatedBy'] is not None):
        extractedData['lastUpdatedBy'] = sourceItem['lastUpdatedBy']
    if ('lastUpdatedDate' in sourceItem) and (sourceItem['lastUpdatedDate'] is not None):
        extractedData['lastUpdatedDate'] = sourceItem['lastUpdatedDate']
    if ('leanUxCanvas' in sourceItem) and (sourceItem['leanUxCanvas'] is not None):
        extractedData['leanUxCanvas'] = sourceItem['leanUxCanvas']
    if ('links' in sourceItem) and (sourceItem['links'] is not None):
        extractedData['links'] = sourceItem['links']
    if ('managerId' in sourceItem) and (sourceItem['managerId'] is not None):
        extractedData['managerId'] = sourceItem['managerId']
    if ('manWeeks' in sourceItem) and (sourceItem['manWeeks'] is not None):
        extractedData['manWeeks'] = sourceItem['manWeeks']
    if ('maxAllocation' in sourceItem) and (sourceItem['maxAllocation'] is not None):
        extractedData['maxAllocation'] = sourceItem['maxAllocation']
    if ('mmf' in sourceItem) and (sourceItem['mmf'] is not None):
        extractedData['mmf'] = sourceItem['mmf']
    if ('mvp' in sourceItem) and (sourceItem['mvp'] is not None):
        extractedData['mvp'] = sourceItem['mvp']
    if ('name' in sourceItem) and (sourceItem['name'] is not None):
        extractedData['name'] = sourceItem['name']
    if ('notes' in sourceItem) and (sourceItem['notes'] is not None):
        extractedData['notes'] = sourceItem['notes']
    if ('notificationStartDate' in sourceItem) and (sourceItem['notificationStartDate'] is not None):
        extractedData['notificationStartDate'] = sourceItem['notificationStartDate']
    if ('notificationFrequency' in sourceItem) and (sourceItem['notificationFrequency'] is not None):
        extractedData['notificationFrequency'] = sourceItem['notificationFrequency']
    if ('notStartedBy' in sourceItem) and (sourceItem['notStartedBy'] is not None):
        extractedData['notStartedBy'] = sourceItem['notStartedBy']
    if ('notStartedDate' in sourceItem) and (sourceItem['notStartedDate'] is not None):
        extractedData['notStartedDate'] = sourceItem['notStartedDate']
    if ('notStartedDateEnd' in sourceItem) and (sourceItem['notStartedDateEnd'] is not None):
        extractedData['notStartedDateEnd'] = sourceItem['notStartedDateEnd']
    if ('overrideVelocity' in sourceItem) and (sourceItem['overrideVelocity'] is not None):
        extractedData['overrideVelocity'] = sourceItem['overrideVelocity']
    if ('owner' in sourceItem) and (sourceItem['owner'] is not None):
        extractedData['owner'] = sourceItem['owner']
    if ('ownerId' in sourceItem) and (sourceItem['ownerId'] is not None):
        extractedData['ownerId'] = sourceItem['ownerId']
    if ('parentId' in sourceItem) and (sourceItem['parentId'] is not None):
        extractedData['parentId'] = sourceItem['parentId']
    if ('parentSplitId' in sourceItem) and (sourceItem['parentSplitId'] is not None):
        extractedData['parentSplitId'] = sourceItem['parentSplitId']
    if ('pendingApprovalBy' in sourceItem) and (sourceItem['pendingApprovalBy'] is not None):
        extractedData['pendingApprovalBy'] = sourceItem['pendingApprovalBy']
    if ('pendingApprovalDate' in sourceItem) and (sourceItem['pendingApprovalDate'] is not None):
        extractedData['pendingApprovalDate'] = sourceItem['pendingApprovalDate']
    if ('planningMode' in sourceItem) and (sourceItem['planningMode'] is not None):
        extractedData['planningMode'] = sourceItem['planningMode']
    if ('plannedValue' in sourceItem) and (sourceItem['plannedValue'] is not None):
        extractedData['plannedValue'] = sourceItem['plannedValue']
    if ('points' in sourceItem) and (sourceItem['points'] is not None):
        extractedData['points'] = sourceItem['points']
    if ('pointsEstimate' in sourceItem) and (sourceItem['pointsEstimate'] is not None):
        extractedData['pointsEstimate'] = sourceItem['pointsEstimate']
    if ('portfolioAskDate' in sourceItem) and (sourceItem['portfolioAskDate'] is not None):
        extractedData['portfolioAskDate'] = sourceItem['portfolioAskDate']
    if ('portfolioId' in sourceItem) and (sourceItem['portfolioId'] is not None):
        extractedData['portfolioId'] = sourceItem['portfolioId']
    if ('predecessorId' in sourceItem) and (sourceItem['predecessorId'] is not None):
        extractedData['predecessorId'] = sourceItem['predecessorId']
    if ('primaryProgramId' in sourceItem) and (sourceItem['primaryProgramId'] is not None):
        extractedData['primaryProgramId'] = sourceItem['primaryProgramId']
    if ('priority' in sourceItem) and (sourceItem['priority'] is not None):
        extractedData['priority'] = sourceItem['priority']
    if ('processStepId' in sourceItem) and (sourceItem['processStepId'] is not None):
        extractedData['processStepId'] = sourceItem['processStepId']
    if ('processStepName' in sourceItem) and (sourceItem['processStepName'] is not None):
        extractedData['processStepName'] = sourceItem['processStepName']
    if ('productId' in sourceItem) and (sourceItem['productId'] is not None):
        extractedData['productId'] = sourceItem['productId']
    if ('productObjectiveIds' in sourceItem) and (sourceItem['productObjectiveIds'] is not None):
        extractedData['productObjectiveIds'] = sourceItem['productObjectiveIds']
    if ('program' in sourceItem) and (sourceItem['program'] is not None):
        extractedData['program'] = sourceItem['program']
    if ('programs' in sourceItem) and (sourceItem['programs'] is not None):
        extractedData['programs'] = sourceItem['programs']
    if ('programId' in sourceItem) and (sourceItem['programId'] is not None):
        extractedData['programId'] = sourceItem['programId']
    if ('programIds' in sourceItem) and (sourceItem['programIds'] is not None):
        extractedData['programIds'] = sourceItem['programIds']
    if ('prototype' in sourceItem) and (sourceItem['prototype'] is not None):
        extractedData['prototype'] = sourceItem['prototype']
    if ('quadrant' in sourceItem) and (sourceItem['quadrant'] is not None):
        extractedData['quadrant'] = sourceItem['quadrant']
    if ('readyToStartBy' in sourceItem) and (sourceItem['readyToStartBy'] is not None):
        extractedData['readyToStartBy'] = sourceItem['readyToStartBy']
    if ('readyToStartDate' in sourceItem) and (sourceItem['readyToStartDate'] is not None):
        extractedData['readyToStartDate'] = sourceItem['readyToStartDate']
    if ('reference' in sourceItem) and (sourceItem['reference'] is not None):
        extractedData['reference'] = sourceItem['reference']
    if ('region' in sourceItem) and (sourceItem['region'] is not None):
        extractedData['region'] = sourceItem['region']
    if ('regionId' in sourceItem) and (sourceItem['regionId'] is not None):
        extractedData['regionId'] = sourceItem['regionId']
    if ('regionIds' in sourceItem) and (sourceItem['regionIds'] is not None):
        extractedData['regionIds'] = sourceItem['regionIds']
    if ('regressionHours' in sourceItem) and (sourceItem['regressionHours'] is not None):
        extractedData['regressionHours'] = sourceItem['regressionHours']
    if ('release' in sourceItem) and (sourceItem['release'] is not None):
        extractedData['release'] = sourceItem['release']
    if ('releaseId' in sourceItem) and (sourceItem['releaseId'] is not None):
        extractedData['releaseId'] = sourceItem['releaseId']
    if ('releaseIds' in sourceItem) and (sourceItem['releaseIds'] is not None):
        extractedData['releaseIds'] = sourceItem['releaseIds']
    if ('releaseNumber' in sourceItem) and (sourceItem['releaseNumber'] is not None):
        extractedData['releaseNumber'] = sourceItem['releaseNumber']
    if ('releaseVehicleIds' in sourceItem) and (sourceItem['releaseVehicleIds'] is not None):
        extractedData['releaseVehicleIds'] = sourceItem['releaseVehicleIds']
    if ('reportColor' in sourceItem) and (sourceItem['reportColor'] is not None):
        extractedData['reportColor'] = sourceItem['reportColor']
    if ('requesterId' in sourceItem) and (sourceItem['requesterId'] is not None):
        extractedData['requesterId'] = sourceItem['requesterId']
    if ('revenueAssurance' in sourceItem) and (sourceItem['revenueAssurance'] is not None):
        extractedData['revenueAssurance'] = sourceItem['revenueAssurance']
    if ('revenueGrowth' in sourceItem) and (sourceItem['revenueGrowth'] is not None):
        extractedData['revenueGrowth'] = sourceItem['revenueGrowth']
    if ('riskAppetite' in sourceItem) and (sourceItem['riskAppetite'] is not None):
        extractedData['riskAppetite'] = sourceItem['riskAppetite']
    if ('riskIds' in sourceItem) and (sourceItem['riskIds'] is not None):
        extractedData['riskIds'] = sourceItem['riskIds']
    if ('roadmap' in sourceItem) and (sourceItem['roadmap'] is not None):
        extractedData['roadmap'] = sourceItem['roadmap']
    if ('roi' in sourceItem) and (sourceItem['roi'] is not None):
        extractedData['roi'] = sourceItem['roi']
    if ('role' in sourceItem) and (sourceItem['role'] is not None):
        extractedData['role'] = sourceItem['role']
    if ('roleId' in sourceItem) and (sourceItem['roleId'] is not None):
        extractedData['roleId'] = sourceItem['roleId']
    if ('scoreCardId' in sourceItem) and (sourceItem['scoreCardId'] is not None):
        extractedData['scoreCardId'] = sourceItem['scoreCardId']
    if ('shortName' in sourceItem) and (sourceItem['shortName'] is not None):
        extractedData['shortName'] = sourceItem['shortName']
    if ('schedule' in sourceItem) and (sourceItem['schedule'] is not None):
        extractedData['schedule'] = sourceItem['schedule']
    if ('scheduleType' in sourceItem) and (sourceItem['scheduleType'] is not None):
        extractedData['scheduleType'] = sourceItem['scheduleType']
    if ('score' in sourceItem) and (sourceItem['score'] is not None):
        extractedData['score'] = sourceItem['score']
    if ('score1' in sourceItem) and (sourceItem['score1'] is not None):
        extractedData['score1'] = sourceItem['score1']
    if ('score2' in sourceItem) and (sourceItem['score2'] is not None):
        extractedData['score2'] = sourceItem['score2']
    if ('score3' in sourceItem) and (sourceItem['score3'] is not None):
        extractedData['score3'] = sourceItem['score3']
    if ('score4' in sourceItem) and (sourceItem['score4'] is not None):
        extractedData['score4'] = sourceItem['score4']
    if ('shortName' in sourceItem) and (sourceItem['shortName'] is not None):
        extractedData['shortName'] = sourceItem['shortName']
    if ('solutionId' in sourceItem) and (sourceItem['solutionId'] is not None):
        extractedData['solutionId'] = sourceItem['solutionId']
    if ('source' in sourceItem) and (sourceItem['source'] is not None):
        extractedData['source'] = sourceItem['source']
    if ('spendToDate' in sourceItem) and (sourceItem['spendToDate'] is not None):
        extractedData['spendToDate'] = sourceItem['spendToDate']
    if ('sprintPrefix' in sourceItem) and (sourceItem['sprintPrefix'] is not None):
        extractedData['sprintPrefix'] = sourceItem['sprintPrefix']
    if ('startDate' in sourceItem) and (sourceItem['startDate'] is not None):
        extractedData['startDate'] = sourceItem['startDate']
    if ('startInitiationDate' in sourceItem) and (sourceItem['startInitiationDate'] is not None):
        extractedData['startInitiationDate'] = sourceItem['startInitiationDate']
    if ('startSprintId' in sourceItem) and (sourceItem['startSprintId'] is not None):
        extractedData['startSprintId'] = sourceItem['startSprintId']
    if ('state' in sourceItem) and (sourceItem['state'] is not None):
        extractedData['state'] = sourceItem['state']
    if ('status' in sourceItem) and (sourceItem['status'] is not None):
        extractedData['status'] = sourceItem['status']
    if ('storyId' in sourceItem) and (sourceItem['storyId'] is not None):
        extractedData['storyId'] = sourceItem['storyId']
    if ('strategicDriver' in sourceItem) and (sourceItem['strategicDriver'] is not None):
        extractedData['strategicDriver'] = sourceItem['strategicDriver']
    if ('strategicHorizon' in sourceItem) and (sourceItem['strategicHorizon'] is not None):
        extractedData['strategicHorizon'] = sourceItem['strategicHorizon']
    if ('strategicValueScore' in sourceItem) and (sourceItem['strategicValueScore'] is not None):
        extractedData['strategicValueScore'] = sourceItem['strategicValueScore']
    if ('tags' in sourceItem) and (sourceItem['tags'] is not None):
        extractedData['tags'] = sourceItem['tags']
    if ('targetCompletionDate' in sourceItem) and (sourceItem['targetCompletionDate'] is not None):
        extractedData['targetCompletionDate'] = sourceItem['targetCompletionDate']
    if ('targetSyncSprintId' in sourceItem) and (sourceItem['targetSyncSprintId'] is not None):
        extractedData['targetSyncSprintId'] = sourceItem['targetSyncSprintId']
    if ('team' in sourceItem) and (sourceItem['team'] is not None):
        extractedData['team'] = sourceItem['team']
    if ('teams' in sourceItem) and (sourceItem['teams'] is not None):
        extractedData['teams'] = sourceItem['teams']
    if ('teamId' in sourceItem) and (sourceItem['teamId'] is not None):
        extractedData['teamId'] = sourceItem['teamId']
    if ('teamIds' in sourceItem) and (sourceItem['teamIds'] is not None):
        extractedData['teamIds'] = sourceItem['teamIds']
    if ('teamDescription' in sourceItem) and (sourceItem['teamDescription'] is not None):
        extractedData['teamDescription'] = sourceItem['teamDescription']
    if ('testCategoryIds' in sourceItem) and (sourceItem['testCategoryIds'] is not None):
        extractedData['testCategoryIds'] = sourceItem['testCategoryIds']
    if ('testCompleteBy' in sourceItem) and (sourceItem['testCompleteBy'] is not None):
        extractedData['testCompleteBy'] = sourceItem['testCompleteBy']
    if ('testCompleteDate' in sourceItem) and (sourceItem['testCompleteDate'] is not None):
        extractedData['testCompleteDate'] = sourceItem['testCompleteDate']
    if ('testSuite' in sourceItem) and (sourceItem['testSuite'] is not None):
        extractedData['testSuite'] = sourceItem['testSuite']
    if ('themeId' in sourceItem) and (sourceItem['themeId'] is not None):
        extractedData['themeId'] = sourceItem['themeId']
    if ('throughput' in sourceItem) and (sourceItem['throughput'] is not None):
        extractedData['throughput'] = sourceItem['throughput']
    if ('tier' in sourceItem) and (sourceItem['tier'] is not None):
        extractedData['tier'] = sourceItem['tier']
    if ('timeApproverId' in sourceItem) and (sourceItem['timeApproverId'] is not None):
        extractedData['timeApproverId'] = sourceItem['timeApproverId']
    if ('timeTrackingRoles' in sourceItem) and (sourceItem['timeTrackingRoles'] is not None):
        extractedData['timeTrackingRoles'] = sourceItem['timeTrackingRoles']
    if ('timeTrackingStartDate' in sourceItem) and (sourceItem['timeTrackingStartDate'] is not None):
        extractedData['timeTrackingStartDate'] = sourceItem['timeTrackingStartDate']
    if ('timeZone' in sourceItem) and (sourceItem['timeZone'] is not None):
        extractedData['timeZone'] = sourceItem['timeZone']
    if ('title' in sourceItem) and (sourceItem['title'] is not None):
        extractedData['title'] = sourceItem['title']
    if ('trackBy' in sourceItem) and (sourceItem['trackBy'] is not None):
        extractedData['trackBy'] = sourceItem['trackBy']      
    if ('totalCapEx' in sourceItem) and (sourceItem['totalCapEx'] is not None):
        extractedData['totalCapEx'] = sourceItem['totalCapEx']
    if ('totalHours' in sourceItem) and (sourceItem['totalHours'] is not None):
        extractedData['totalHours'] = sourceItem['totalHours']
    if ('totalOpEx' in sourceItem) and (sourceItem['totalOpEx'] is not None):
        extractedData['totalOpEx'] = sourceItem['totalOpEx']
    if ('type' in sourceItem) and (sourceItem['type'] is not None):
        extractedData['type'] = sourceItem['type']
    if ('uid' in sourceItem) and (sourceItem['uid'] is not None):
        extractedData['uid'] = sourceItem['uid']
    if ('userEndDate' in sourceItem) and (sourceItem['userEndDate'] is not None):
        extractedData['userEndDate'] = sourceItem['userEndDate']
    if ('userStartDate' in sourceItem) and (sourceItem['userStartDate'] is not None):
        extractedData['userStartDate'] = sourceItem['userStartDate']
    if ('userType' in sourceItem) and (sourceItem['userType'] is not None):
        extractedData['userType'] = sourceItem['userType']
    if ('valuePoints' in sourceItem) and (sourceItem['valuePoints'] is not None):
        extractedData['valuePoints'] = sourceItem['valuePoints']
    if ('vehicleId' in sourceItem) and (sourceItem['vehicleId'] is not None):
        extractedData['vehicleId'] = sourceItem['vehicleId']
    if ('viewPublicErs' in sourceItem) and (sourceItem['viewPublicErs'] is not None):
        extractedData['viewPublicErs'] = sourceItem['viewPublicErs']
    if ('workCodeId' in sourceItem) and (sourceItem['workCodeId'] is not None):
        extractedData['workCodeId'] = sourceItem['workCodeId']
    if ('yearlyCashFlow1' in sourceItem) and (sourceItem['yearlyCashFlow1'] is not None):
        extractedData['yearlyCashFlow1'] = sourceItem['yearlyCashFlow1']
        
def ExtractItemDataOLD(itemType, sourceItem, extractedData):
    """ PREVIOUS VERSION
        Extract all applicable fields from the source item and add them to the extracted
        data, based on item type.

    Args:
        itemType: Which type of work the sourceItem is: epics, features, stories, defects, tasks, programs
        sourceItem: Full set of data for this item from Jira Align
        extractedData: All the data that needs to be saved from this sourceItem
    """
    # Common fields for all item types
    extractedData['itemtype'] = itemType
    if ('description' in sourceItem) and (sourceItem['description'] is not None):
        extractedData['description'] = sourceItem['description']
    extractedData['id'] = sourceItem['id']
    
    # Fields that exist only for Programs
    if (itemType == 'programs'):
        if sourceItem['caseDevelopmentId'] is not None:
            extractedData['caseDevelopmentId'] = sourceItem['caseDevelopmentId']
        extractedData['intakeFormId'] = sourceItem['intakeFormId']
        extractedData['isSolution'] = sourceItem['isSolution']
        if sourceItem['lastUpdatedDate'] is not None:
            extractedData['lastUpdatedDate'] = sourceItem['lastUpdatedDate']
        extractedData['portfolioId'] = sourceItem['portfolioId']
        extractedData['regionId'] = sourceItem['regionId']
        extractedData['scoreCardId'] = sourceItem['scoreCardId']
        extractedData['solutionId'] = sourceItem['solutionId']
        extractedData['teamId'] = sourceItem['teamId']
        extractedData['teamDescription'] = sourceItem['teamDescription']
        extractedData['title'] = sourceItem['title']
        return
        
    # Fields that exist only for Releases/PIs
    if (itemType == 'releases'):
        extractedData['id'] = sourceItem['id']
        extractedData['title'] = sourceItem['title']
        extractedData['shortName'] = sourceItem['shortName']
        extractedData['type'] = sourceItem['type']
        extractedData['status'] = sourceItem['status']
        extractedData['description'] = sourceItem['description']
        extractedData['releaseNumber'] = sourceItem['releaseNumber']
        extractedData['scheduleType'] = sourceItem['scheduleType']
        extractedData['roadmap'] = sourceItem['roadmap']
        extractedData['budget'] = sourceItem['budget']
        extractedData['health'] = sourceItem['health']
        if sourceItem['createDate'] is not None:
            extractedData['createDate'] = sourceItem['createDate']
        if sourceItem['startDate'] is not None:
            extractedData['startDate'] = sourceItem['startDate']
        if sourceItem['endDate'] is not None:
            extractedData['endDate'] = sourceItem['endDate']
        if sourceItem['testSuite'] is not None:
            extractedData['testSuite'] = sourceItem['testSuite']
        if sourceItem['portfolioId'] is not None:
            extractedData['portfolioId'] = sourceItem['portfolioId']
        if sourceItem['predecessorId'] is not None:
            extractedData['predecessorId'] = sourceItem['predecessorId']
        if sourceItem['score1'] is not None:
            extractedData['score1'] = sourceItem['score1']
        if sourceItem['score2'] is not None:
            extractedData['score2'] = sourceItem['score2']
        if sourceItem['score3'] is not None:
            extractedData['score3'] = sourceItem['score3']
        if sourceItem['score4'] is not None:
            extractedData['score4'] = sourceItem['score4']
        if sourceItem['blendedHourlyRate'] is not None:
            extractedData['blendedHourlyRate'] = sourceItem['blendedHourlyRate']
        if sourceItem['divisionId'] is not None:
            extractedData['divisionId'] = sourceItem['divisionId']
        if sourceItem['programIds'] is not None:
            extractedData['programIds'] = sourceItem['programIds']
        if ('regionIds' in sourceItem) and (sourceItem['regionIds'] is not None):
            extractedData['regionIds'] = sourceItem['regionIds']
        if ('anchorSprintIds' in sourceItem) and (sourceItem['anchorSprintIds'] is not None):
            extractedData['anchorSprintIds'] = sourceItem['anchorSprintIds']
        if sourceItem['lastUpdatedBy'] is not None:
            extractedData['lastUpdatedBy'] = sourceItem['lastUpdatedBy']
        if sourceItem['lastUpdatedDate'] is not None:
            extractedData['lastUpdatedDate'] = sourceItem['lastUpdatedDate']
        if sourceItem['releaseNumber'] is not None:
            extractedData['releaseNumber'] = sourceItem['releaseNumber']
        return
    
    # Fields that exist only for Sprints/Iterations
    if itemType == 'iterations':
        extractedData['id'] = sourceItem['id']
        extractedData['releaseId'] = sourceItem['releaseId']
        extractedData['title'] = sourceItem['title']
        extractedData['shortName'] = sourceItem['shortName']
        extractedData['schedule'] = sourceItem['schedule']
        extractedData['state'] = sourceItem['state']
        extractedData['teamId'] = sourceItem['teamId']
        extractedData['maxAllocation'] = sourceItem['maxAllocation']
        extractedData['color'] = sourceItem['color']
        extractedData['isLocked'] = sourceItem['isLocked']
        extractedData['defectAllocation'] = sourceItem['defectAllocation']
        extractedData['programId'] = sourceItem['programId']
        extractedData['regionId'] = sourceItem['regionId']
        extractedData['type'] = sourceItem['type']
        if sourceItem['beginDate'] is not None:
            extractedData['beginDate'] = sourceItem['beginDate']
        if sourceItem['endDate'] is not None:
            extractedData['endDate'] = sourceItem['endDate']
        if sourceItem['actualEndDate'] is not None:
            extractedData['actualEndDate'] = sourceItem['actualEndDate']
        if sourceItem['description'] is not None:
            extractedData['description'] = sourceItem['description']
        if sourceItem['overrideVelocity'] is not None:
            extractedData['overrideVelocity'] = sourceItem['overrideVelocity']
        if sourceItem['createDate'] is not None:
            extractedData['createDate'] = sourceItem['createDate']
        if sourceItem['goal'] is not None:
            extractedData['goal'] = sourceItem['goal']
        if sourceItem['anchorSprintId'] is not None:
            extractedData['anchorSprintId'] = sourceItem['anchorSprintId']
        if sourceItem['regressionHours'] is not None:
            extractedData['regressionHours'] = sourceItem['regressionHours']
        if sourceItem['lastUpdatedDate'] is not None:
            extractedData['lastUpdatedDate'] = sourceItem['lastUpdatedDate']

    # Fields that exist only for Teams
    if itemType == 'teams':
        extractedData['id'] = sourceItem['id']
        extractedData['name'] = sourceItem['name']
        extractedData['ownerId'] = sourceItem['ownerId']
        extractedData['isActive'] = sourceItem['isActive']
        if sourceItem['regionId'] is not None:
            extractedData['regionId'] = sourceItem['regionId']
        if sourceItem['programId'] is not None:
            extractedData['programId'] = sourceItem['programId']
        if sourceItem['programIds'] is not None:
            extractedData['programIds'] = sourceItem['programIds']
        if sourceItem['description'] is not None:
            extractedData['description'] = sourceItem['description']
        if sourceItem['sprintPrefix'] is not None:
            extractedData['sprintPrefix'] = sourceItem['sprintPrefix']
        if sourceItem['shortName'] is not None:
            extractedData['shortName'] = sourceItem['shortName']
        if sourceItem['trackBy'] is not None:
            extractedData['trackBy'] = sourceItem['trackBy']
        if sourceItem['maxAllocation'] is not None:
            extractedData['maxAllocation'] = sourceItem['maxAllocation']
        if sourceItem['allowTaskDeletion'] is not None:
            extractedData['allowTaskDeletion'] = sourceItem['allowTaskDeletion']
        if sourceItem['allowTeamToRunStandup'] is not None:
            extractedData['allowTeamToRunStandup'] = sourceItem['allowTeamToRunStandup']
        if sourceItem['isKanbanTeam'] is not None:
            extractedData['isKanbanTeam'] = sourceItem['isKanbanTeam']
        if sourceItem['createDate'] is not None:
            extractedData['createDate'] = sourceItem['createDate']
        if sourceItem['lastUpdatedDate'] is not None:
            extractedData['lastUpdatedDate'] = sourceItem['lastUpdatedDate']
        if sourceItem['enableAutoEstimate'] is not None:
            extractedData['enableAutoEstimate'] = sourceItem['enableAutoEstimate']
        if sourceItem['autoEstimateValue'] is not None:
            extractedData['autoEstimateValue'] = sourceItem['autoEstimateValue']
        if sourceItem['throughput'] is not None:
            extractedData['throughput'] = sourceItem['throughput']
        if sourceItem['communityIds'] is not None:
            extractedData['communityIds'] = sourceItem['communityIds']
        
    if itemType != "themegroups":
        if sourceItem['createDate'] is not None:
            extractedData['createDate'] = sourceItem['createDate']

    # Fields that exist for all types other than objectives
    if itemType != "objectives":
        if (itemType != "themegroups") and (itemType != "teams"):
            if ('createdBy' in sourceItem) and (sourceItem['createdBy'] is not None):
                extractedData['createdBy'] = sourceItem['createdBy']
            extractedData['state'] = sourceItem['state']
            extractedData['title'] = sourceItem['title']
        
    # Fields that exist for all types other than tasks and objectives and themese
    if (itemType != "tasks") and (itemType != "objectives") and (itemType != "themes") and\
        (itemType != "themegroups") and (itemType != "iterations") and (itemType != "teams"):
        if sourceItem['tags'] is not None:
            extractedData['tags'] = sourceItem['tags']

    # Fields that exist for all types other than defects or themes
    if (itemType != "defects") and (itemType != "themes") and (itemType != "iterations") and (itemType != "teams"):
        if sourceItem['lastUpdatedBy'] is not None:
            extractedData['lastUpdatedBy'] = sourceItem['lastUpdatedBy']
        if itemType != "themegroups":
            if sourceItem['ownerId'] is not None:
                extractedData['ownerId'] = sourceItem['ownerId']

    # Fields that exist for all types other than defects and tasks
    if (itemType != "defects") and (itemType != "tasks") and (itemType != "objectives") and\
       (itemType != "iterations") and (itemType != "teams"):
        if itemType != "themegroups":
            if sourceItem['processStepId'] is not None:
                extractedData['processStepId'] = sourceItem['processStepId']
    
    # Specific fields to extract for each item type
    if (itemType == "epics") or (itemType == "features") or (itemType == "capabilities"):
        if sourceItem['acceptedDate'] is not None:
            extractedData['acceptedDate'] = sourceItem['acceptedDate']
        if sourceItem['acceptedUserId'] is not None:
            extractedData['acceptedUserId'] = sourceItem['acceptedUserId']
        if sourceItem['inProgressBy'] is not None:
            extractedData['inProgressBy'] = sourceItem['inProgressBy']
        if sourceItem['inProgressDate'] is not None:
            extractedData['inProgressDate'] = sourceItem['inProgressDate']
        if sourceItem['points'] is not None:
            extractedData['points'] = sourceItem['points']
        if sourceItem['portfolioAskDate'] is not None:
            extractedData['portfolioAskDate'] = sourceItem['portfolioAskDate']
        extractedData['primaryProgramId'] = sourceItem['primaryProgramId']
        if sourceItem['processStepId'] is not None:
            extractedData['processStepId'] = sourceItem['processStepId']
        if sourceItem['startInitiationDate'] is not None:
            extractedData['startInitiationDate'] = sourceItem['startInitiationDate']
        if sourceItem['targetCompletionDate'] is not None:
            extractedData['targetCompletionDate'] = sourceItem['targetCompletionDate']

    if (itemType == "capabilities") or (itemType == "features"):
        if sourceItem['parentId'] is not None:
            extractedData['parentId'] = sourceItem['parentId']
        if sourceItem['type'] is not None:
            extractedData['type'] = sourceItem['type']
        
    if (itemType == "epics") or (itemType == "features"):
        if sourceItem['additionalProgramIds'] is not None:
            extractedData['additionalProgramIds'] = sourceItem['additionalProgramIds']
        if sourceItem['budget'] is not None:
            extractedData['budget'] = sourceItem['budget']
        if sourceItem['businessImpact'] is not None:
            extractedData['businessImpact'] = sourceItem['businessImpact']
        if sourceItem['connectorId'] is not None:
            extractedData['connectorId'] = sourceItem['connectorId']
        if sourceItem['designStage'] is not None:
            extractedData['designStage'] = sourceItem['designStage']
        if sourceItem['discountRate'] is not None:
            extractedData['discountRate'] = sourceItem['discountRate']
        if sourceItem['estimateAtCompletion'] is not None:
            extractedData['estimateAtCompletion'] = sourceItem['estimateAtCompletion']
        if sourceItem['externalCapEx'] is not None:
            extractedData['externalCapEx'] = sourceItem['externalCapEx']
        if sourceItem['externalId'] is not None:
            extractedData['externalId'] = sourceItem['externalId']
        if sourceItem['externalOpEx'] is not None:
            extractedData['externalOpEx'] = sourceItem['externalOpEx']
        if sourceItem['externalProject'] is not None:
            extractedData['externalProject'] = sourceItem['externalProject']
        if sourceItem['failureImpact'] is not None:
            extractedData['failureImpact'] = sourceItem['failureImpact']
        if sourceItem['failureProbability'] is not None:
            extractedData['failureProbability'] = sourceItem['failureProbability']
        if sourceItem['forecastYears'] is not None:
            extractedData['forecastYears'] = sourceItem['forecastYears']
        if sourceItem['hypothesis'] is not None:
            extractedData['hypothesis'] = sourceItem['hypothesis']
        if sourceItem['initialInvestment'] is not None:
            extractedData['initialInvestment'] = sourceItem['initialInvestment']
        if sourceItem['isSplit'] is not None:
            extractedData['isSplit'] = sourceItem['isSplit']
        if sourceItem['leanUxCanvas'] is not None:
            extractedData['leanUxCanvas'] = sourceItem['leanUxCanvas']
        if sourceItem['links'] is not None:
            extractedData['links'] = sourceItem['links']
        if sourceItem['parentSplitId'] is not None:
            extractedData['parentSplitId'] = sourceItem['parentSplitId']
        if sourceItem['processStepName'] is not None:
            extractedData['processStepName'] = sourceItem['processStepName']
        if sourceItem['prototype'] is not None:
            extractedData['prototype'] = sourceItem['prototype']
        if sourceItem['riskAppetite'] is not None:
            extractedData['riskAppetite'] = sourceItem['riskAppetite']
        if sourceItem['spendToDate'] is not None:
            extractedData['spendToDate'] = sourceItem['spendToDate']
        if sourceItem['themeId'] is not None:
            extractedData['themeId'] = sourceItem['themeId']
        if sourceItem['totalCapEx'] is not None:
            extractedData['totalCapEx'] = sourceItem['totalCapEx']
        if sourceItem['totalOpEx'] is not None:
            extractedData['totalOpEx'] = sourceItem['totalOpEx']
        if sourceItem['workCodeId'] is not None:
            extractedData['workCodeId'] = sourceItem['workCodeId']

    if itemType == "epics":
        extractedData['themeId'] = sourceItem['themeId']
        extractedData['primaryProgramId'] = sourceItem['primaryProgramId']
        extractedData['type'] = sourceItem['type']
        if sourceItem['epicObjectId'] is not None:
            extractedData['epicObjectId'] = sourceItem['epicObjectId']
        if sourceItem['themeId'] is not None:
            extractedData['themeId'] = sourceItem['themeId']
        if sourceItem['strategicDriver'] is not None:
            extractedData['strategicDriver'] = sourceItem['strategicDriver']
        if sourceItem['strategicValueScore'] is not None:
            extractedData['strategicValueScore'] = sourceItem['strategicValueScore']
        if sourceItem['points'] is not None:
            extractedData['points'] = sourceItem['points']
        if sourceItem['fcastShare'] is not None:
            extractedData['fcastShare'] = sourceItem['fcastShare']
        if sourceItem['investmentType'] is not None:
            extractedData['investmentType'] = sourceItem['investmentType']
        if sourceItem['notStartedBy'] is not None:
            extractedData['notStartedBy'] = sourceItem['notStartedBy']
        if sourceItem['notStartedDate'] is not None:
            extractedData['notStartedDate'] = sourceItem['notStartedDate']
        if sourceItem['notStartedDateEnd'] is not None:
            extractedData['notStartedDateEnd'] = sourceItem['notStartedDateEnd']
        if sourceItem['yearlyCashFlow1'] is not None:
            extractedData['yearlyCashFlow1'] = sourceItem['yearlyCashFlow1']
        if sourceItem['planningMode'] is not None:
            extractedData['planningMode'] = sourceItem['planningMode']
        if sourceItem['customerIds'] is not None:
            extractedData['customerIds'] = sourceItem['customerIds']
        if sourceItem['epicObjectId'] is not None:
            extractedData['epicObjectId'] = sourceItem['epicObjectId']
        if sourceItem['capitalized'] is not None:
            extractedData['capitalized'] = sourceItem['capitalized']
        if sourceItem['efficiencyDividend'] is not None:
            extractedData['efficiencyDividend'] = sourceItem['efficiencyDividend']
        if sourceItem['revenueAssurance'] is not None:
            extractedData['revenueAssurance'] = sourceItem['revenueAssurance']
        if sourceItem['roi'] is not None:
            extractedData['roi'] = sourceItem['roi']
        if sourceItem['effortSwag'] is not None:
            extractedData['effortSwag'] = sourceItem['effortSwag']
        if sourceItem['abilityToExec'] is not None:
            extractedData['abilityToExec'] = sourceItem['abilityToExec']
        if sourceItem['additionalProcessStepIds'] is not None:
            extractedData['additionalProcessStepIds'] = sourceItem['additionalProcessStepIds']
        if sourceItem['externalKey'] is not None:
            extractedData['externalKey'] = sourceItem['externalKey']
        if sourceItem['fundingStage'] is not None:
            extractedData['fundingStage'] = sourceItem['fundingStage']
        if sourceItem['quadrant'] is not None:
            extractedData['quadrant'] = sourceItem['quadrant']
        if sourceItem['strategicHorizon'] is not None:
            extractedData['strategicHorizon'] = sourceItem['strategicHorizon']
        if sourceItem['isCanceled'] is not None:
            extractedData['isCanceled'] = sourceItem['isCanceled']
        if sourceItem['isRecycled'] is not None:
            extractedData['isRecycled'] = sourceItem['isRecycled']
        if 'dependencyIds' in sourceItem:
            if sourceItem['dependencyIds'] is not None:
                extractedData['dependencyIds'] = sourceItem['dependencyIds']
        if 'featureIds' in sourceItem:
            if sourceItem['featureIds'] is not None:
                extractedData['featureIds'] = sourceItem['featureIds']
        if sourceItem['health'] is not None:
            extractedData['health'] = sourceItem['health']
        if sourceItem['status'] is not None:
            extractedData['status'] = sourceItem['status']
        if sourceItem['customFields'] is not None:
            extractedData['customFields'] = sourceItem['customFields']
        if sourceItem['inProgressDateEnd'] is not None:
            extractedData['inProgressDateEnd'] = sourceItem['inProgressDateEnd']
        if sourceItem['reportColor'] is not None:
            extractedData['reportColor'] = sourceItem['reportColor']
        if sourceItem['itRisk'] is not None:
            extractedData['itRisk'] = sourceItem['itRisk']
        if sourceItem['releaseIds'] is not None:
            extractedData['releaseIds'] = sourceItem['releaseIds']
        if sourceItem['customFields'] is not None:
            extractedData['customFields'] = sourceItem['customFields']
        if sourceItem['mvp'] is not None:
            extractedData['mvp'] = sourceItem['mvp']
            
    elif itemType == "capabilities":
        if sourceItem['reportColor'] is not None:
            extractedData['reportColor'] = sourceItem['reportColor']
        pass
    
    elif itemType == "features":
        if sourceItem['isBlocked'] is not None:
            extractedData['isBlocked'] = sourceItem['isBlocked']
        if sourceItem['isMultiProgram'] is not None:
            extractedData['isMultiProgram'] = sourceItem['isMultiProgram']
        if sourceItem['mmf'] is not None:
            extractedData['mmf'] = sourceItem['mmf']
        if sourceItem['parentId'] is not None:
            extractedData['parentId'] = sourceItem['parentId']
        if sourceItem['priority'] is not None:
            extractedData['priority'] = sourceItem['priority']
        if sourceItem['primaryProgramId'] is not None:
            extractedData['primaryProgramId'] = sourceItem['primaryProgramId']
        if sourceItem['points'] is not None:
            extractedData['points'] = sourceItem['points']
        if sourceItem['score'] is not None:
            extractedData['score'] = sourceItem['score']
        if sourceItem['processStepId'] is not None:
            extractedData['processStepId'] = sourceItem['processStepId']
        if sourceItem['productId'] is not None:
            extractedData['productId'] = sourceItem['productId']
        if sourceItem['reportColor'] is not None:
            extractedData['reportColor'] = sourceItem['reportColor']
        if sourceItem['releaseId'] is not None:
            extractedData['releaseId'] = sourceItem['releaseId']
        if sourceItem['isBlocked'] is not None:
            extractedData['isBlocked'] = sourceItem['isBlocked']
        if sourceItem['priority'] is not None:
            extractedData['priority'] = sourceItem['priority']
        if sourceItem['isMultiProgram'] is not None:
            extractedData['isMultiProgram'] = sourceItem['isMultiProgram']
        if sourceItem['startSprintId'] is not None:
            extractedData['startSprintId'] = sourceItem['startSprintId']
        if sourceItem['endSprintId'] is not None:
            extractedData['endSprintId'] = sourceItem['endSprintId']
        if sourceItem['category'] is not None:
            extractedData['category'] = sourceItem['category']
        if sourceItem['businessDriver'] is not None:
            extractedData['businessDriver'] = sourceItem['businessDriver']
        if sourceItem['divisionId'] is not None:
            extractedData['divisionId'] = sourceItem['divisionId']
        if sourceItem['functionalArea'] is not None:
            extractedData['functionalArea'] = sourceItem['functionalArea']
        if sourceItem['capitalized'] is not None:
            extractedData['capitalized'] = sourceItem['capitalized']
        if sourceItem['source'] is not None:
            extractedData['source'] = sourceItem['source']
        if sourceItem['customerIds'] is not None:
            extractedData['customerIds'] = sourceItem['customerIds']
        if sourceItem['requesterId'] is not None:
            extractedData['requesterId'] = sourceItem['requesterId']
        if sourceItem['associatedTicket'] is not None:
            extractedData['associatedTicket'] = sourceItem['associatedTicket']
        if sourceItem['benefits'] is not None:
            extractedData['benefits'] = sourceItem['benefits']
        if sourceItem['blockedReason'] is not None:
            extractedData['blockedReason'] = sourceItem['blockedReason']
        if sourceItem['score'] is not None:
            extractedData['score'] = sourceItem['score']
        if sourceItem['acceptedDate'] is not None:
            extractedData['acceptedDate'] = sourceItem['acceptedDate']
        if sourceItem['acceptedUserId'] is not None:
            extractedData['acceptedUserId'] = sourceItem['acceptedUserId']
        if sourceItem['pendingApprovalBy'] is not None:
            extractedData['pendingApprovalBy'] = sourceItem['pendingApprovalBy']
        if sourceItem['pendingApprovalDate'] is not None:
            extractedData['pendingApprovalDate'] = sourceItem['pendingApprovalDate']
        if sourceItem['readyToStartBy'] is not None:
            extractedData['readyToStartBy'] = sourceItem['readyToStartBy']
        if sourceItem['readyToStartDate'] is not None:
            extractedData['readyToStartDate'] = sourceItem['readyToStartDate']
        if sourceItem['inProgressBy'] is not None:
            extractedData['inProgressBy'] = sourceItem['inProgressBy']
        if sourceItem['inProgressDate'] is not None:
            extractedData['inProgressDate'] = sourceItem['inProgressDate']
        if sourceItem['devCompleteBy'] is not None:
            extractedData['devCompleteBy'] = sourceItem['devCompleteBy']
        if sourceItem['devCompleteDate'] is not None:
            extractedData['devCompleteDate'] = sourceItem['devCompleteDate']
        if sourceItem['testCompleteBy'] is not None:
            extractedData['testCompleteBy'] = sourceItem['testCompleteBy']
        if sourceItem['testCompleteDate'] is not None:
            extractedData['testCompleteDate'] = sourceItem['testCompleteDate']
        if sourceItem['isRecycled'] is not None:
            extractedData['isRecycled'] = sourceItem['isRecycled']
        if sourceItem['iterationSort'] is not None:
            extractedData['iterationSort'] = sourceItem['iterationSort']
        if sourceItem['complexity'] is not None:
            extractedData['complexity'] = sourceItem['complexity']
        if sourceItem['businessValue'] is not None:
            extractedData['businessValue'] = sourceItem['businessValue']
        if sourceItem['externalUser'] is not None:
            extractedData['externalUser'] = sourceItem['externalUser']
        if sourceItem['points'] is not None:
            extractedData['points'] = sourceItem['points']
        if sourceItem['vehicleId'] is not None:
            extractedData['vehicleId'] = sourceItem['vehicleId']
        if sourceItem['processStepId'] is not None:
            extractedData['processStepId'] = sourceItem['processStepId']
        if sourceItem['processStepName'] is not None:
            extractedData['processStepName'] = sourceItem['processStepName']
        if sourceItem['additionalProcessStepIds'] is not None:
            extractedData['additionalProcessStepIds'] = sourceItem['additionalProcessStepIds']
        if sourceItem['manWeeks'] is not None:
            extractedData['manWeeks'] = sourceItem['manWeeks']
        if sourceItem['isImport'] is not None:
            extractedData['isImport'] = sourceItem['isImport']
        if sourceItem['externalKey'] is not None:
            extractedData['externalKey'] = sourceItem['externalKey']
        if sourceItem['estimateTshirt'] is not None:
            extractedData['estimateTshirt'] = sourceItem['estimateTshirt']
        if sourceItem['itrisk'] is not None:
            extractedData['itrisk'] = sourceItem['itrisk']
        if sourceItem['jiraProjectKey'] is not None:
            extractedData['jiraProjectKey'] = sourceItem['jiraProjectKey']
        if sourceItem['featureSummary'] is not None:
            extractedData['featureSummary'] = sourceItem['featureSummary']
        if sourceItem['featureRank'] is not None:
            extractedData['featureRank'] = sourceItem['featureRank']
        if sourceItem['descriptionRich'] is not None:
            extractedData['descriptionRich'] = sourceItem['descriptionRich']
        if sourceItem['inScope'] is not None:
            extractedData['inScope'] = sourceItem['inScope']
        if sourceItem['revenueGrowth'] is not None:
            extractedData['revenueGrowth'] = sourceItem['revenueGrowth']
        if sourceItem['expenseSavings'] is not None:
            extractedData['expenseSavings'] = sourceItem['expenseSavings']
        if sourceItem['estimationEffortPercent'] is not None:
            extractedData['estimationEffortPercent'] = sourceItem['estimationEffortPercent']
        if sourceItem['isCanceled'] is not None:
            extractedData['isCanceled'] = sourceItem['isCanceled']
        if sourceItem['itemToSyncDate'] is not None:
            extractedData['itemToSyncDate'] = sourceItem['itemToSyncDate']
        if sourceItem['releaseVehicleIds'] is not None:
            extractedData['releaseVehicleIds'] = sourceItem['releaseVehicleIds']
        if sourceItem['productObjectiveIds'] is not None:
            extractedData['productObjectiveIds'] = sourceItem['productObjectiveIds']
        if sourceItem['affectedCountryIds'] is not None:
            extractedData['affectedCountryIds'] = sourceItem['affectedCountryIds']
        if sourceItem['testCategoryIds'] is not None:
            extractedData['testCategoryIds'] = sourceItem['testCategoryIds']

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
        if ('externalKey' in sourceItem) and (sourceItem['externalKey'] is not None):
            extractedData['externalKey'] = sourceItem['externalKey']

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
            
    elif itemType == "objectives":
        extractedData['id'] = sourceItem['id']
        extractedData['tier'] = sourceItem['tier']
        extractedData['programId'] = sourceItem['programId']
        extractedData['type'] = sourceItem['type']
        extractedData['isBlocked'] = sourceItem['isBlocked']
        extractedData['ownerId'] = sourceItem['ownerId']
        extractedData['name'] = sourceItem['name']
        extractedData['description'] = sourceItem['description']
        if sourceItem['createDate'] is not None:
            extractedData['createDate'] = sourceItem['createDate']
        if sourceItem['status'] is not None:
            extractedData['status'] = sourceItem['status']
        if sourceItem['notes'] is not None:
            extractedData['notes'] = sourceItem['notes']
        if sourceItem['startInitiationDate'] is not None:
            extractedData['startInitiationDate'] = sourceItem['startInitiationDate']
        if sourceItem['endDate'] is not None:
            extractedData['endDate'] = sourceItem['endDate']
        if sourceItem['category'] is not None:
            extractedData['category'] = sourceItem['category']
        if sourceItem['targetSyncSprintId'] is not None:
            extractedData['targetSyncSprintId'] = sourceItem['targetSyncSprintId']
        if sourceItem['plannedValue'] is not None:
            extractedData['plannedValue'] = sourceItem['plannedValue']
        if sourceItem['deliveredValue'] is not None:
            extractedData['deliveredValue'] = sourceItem['deliveredValue']
        if sourceItem['themeId'] is not None:
            extractedData['themeId'] = sourceItem['themeId']
        if sourceItem['blockedReason'] is not None:
            extractedData['blockedReason'] = sourceItem['blockedReason']
        if sourceItem['lastUpdatedDate'] is not None:
            extractedData['lastUpdatedDate'] = sourceItem['lastUpdatedDate']
        if sourceItem['lastUpdatedBy'] is not None:
            extractedData['lastUpdatedBy'] = sourceItem['lastUpdatedBy']
        if sourceItem['targetCompletionDate'] is not None:
            extractedData['targetCompletionDate'] = sourceItem['targetCompletionDate']
        if sourceItem['portfolioAskDate'] is not None:
            extractedData['portfolioAskDate'] = sourceItem['portfolioAskDate']
        if sourceItem['health'] is not None:
            extractedData['health'] = sourceItem['health']
        if sourceItem['parentId'] is not None:
            extractedData['parentId'] = sourceItem['parentId']
        if sourceItem['score'] is not None:
            extractedData['score'] = sourceItem['score']
        if sourceItem['portfolioId'] is not None:
            extractedData['portfolioId'] = sourceItem['portfolioId']
        if sourceItem['goalId'] is not None:
            extractedData['goalId'] = sourceItem['goalId']
        if sourceItem['solutionId'] is not None:
            extractedData['solutionId'] = sourceItem['solutionId']
        if sourceItem['notificationStartDate'] is not None:
            extractedData['notificationStartDate'] = sourceItem['notificationStartDate']
        if sourceItem['notificationFrequency'] is not None:
            extractedData['notificationFrequency'] = sourceItem['notificationFrequency']
        if sourceItem['reference'] is not None:
            extractedData['reference'] = sourceItem['reference']
        if sourceItem['programIds'] is not None:
            extractedData['programIds'] = sourceItem['programIds']
        if sourceItem['releaseIds'] is not None:
            extractedData['releaseIds'] = sourceItem['releaseIds']
        if sourceItem['featureIds'] is not None:
            extractedData['featureIds'] = sourceItem['featureIds']
        if sourceItem['impedimentIds'] is not None:
            extractedData['impedimentIds'] = sourceItem['impedimentIds']
        if sourceItem['riskIds'] is not None:
            extractedData['riskIds'] = sourceItem['riskIds']
        if sourceItem['dependencyIds'] is not None:
            extractedData['dependencyIds'] = sourceItem['dependencyIds']
        if sourceItem['customFields'] is not None:
            extractedData['customFields'] = sourceItem['customFields']
        if sourceItem['teamIds'] is not None:
            extractedData['teamIds'] = sourceItem['teamIds']
        
def ReadAllItems(which, maxToRead, filterOnProgramID=None):
    """ Read in all work items of the given type (Epic, Feature, Story, etc.) and 
        return selected fields of them to the caller.  This is NOT a complete dump of all data.
        Any work items that are deleted/in recycle bin are skipped.
    Args:
        which: Which type of work items to retrieve.  
               Valid values are: epics, capabilities, features, stories, defects, tasks
        maxToRead: Maximum number of entries to read in.
        filterOnProgramID: If not None, then check the read in item with the given
        Program ID, and skip processing it if it does not match.
    """
    print("Collecting up to " + str(maxToRead) + " items of type " + which + "...")
    itemArr = []

    # Get the first set of data, which may be everything or may not be
    fullUrl = cfg.instanceurl + "/" + which + "?expand=true"
    items = GetFromJiraAlign(True, fullUrl)
    Data = items.json()
    line_count = 0
    # Starting point for skipping is to go to the next 100..
    skip = 100

    while Data != None:
        for eachWorkItem in Data:
            if 'isRecycled' in eachWorkItem:
                itemIsDel = eachWorkItem['isRecycled']
            else:
                itemIsDel = False
            # ONLY Take items that are not in the recycle bin/deleted
            if itemIsDel is True:
                continue;
            
            # If we want to filter on Program ID, then make sure it matches
            # before processing it.  If it's not processed, then it won't be
            # in the output.
            if (filterOnProgramID is not None):
                if (eachWorkItem['programId'] != filterOnProgramID):
                    continue
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
