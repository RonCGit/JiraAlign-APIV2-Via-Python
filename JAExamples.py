#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 30 10:50:05 2020
@author: roncavallo
See README for usage instructions
"""
from urllib.parse import urlparse

#import subfiles
import workitemparser
import common
import creds
import cfg

####################################################################################################################################################################################
def main():
####################################################################################################################################################################################
# MAIN
  
    # Call a subfile that helps handle shared routines and variables between this file and other files like workitemparser, jathemes, etc
    cfg.init()
    
    #Collect api server and endpoint. Also collect all of the instance json infomation we need into arrays with CollectUsrMenuItems
    common.CollectApiInfo()
    #print(instanceurl+apiendpoint)
 
    #Collects information you will need later if you want to create users at all, and in some cases work items.
    common.CollectBasicItems()

    # Read in all Capabilities
    common.Capability()

    # Read in all Products
    common.Product()

    # Read in all Programs
    common.Program()

    # Read in all Users
    common.User()

    # Read in all iterations
    common.Iterations()

    # Print first (up to) 5 regions
    common.PrintXRegions(5)

    # Print first (up to) 5 cities
    common.PrintXCities(5)

    # Print first (up to) 5 capabilities
    common.PrintXCapabilities(5)

    # Print first (up to) 5 programs
    common.PrintXPrograms(5)

    # Print first (up to) 5 products
    common.PrintXProducts(5)

    # Print first (up to) 5 users
    common.PrintXUsers(5)

    # Print first (up to) 5 iterations
    common.PrintXIterations(5)

    #Features
    if "features" in cfg.apiendpoint:     
        common.Product()
        # Call Feature from the workitemparser file so that you can build the complete list of Features into an array
        workitemparser.FeatsOrCaps("features")
        # Call the FeatRoutine that utilizes the array that is created in Features and puts them into a csv file.
        common.Program()
        common.FeatRoutine()
    
    #Capabilities
    if "capabilities" in cfg.apiendpoint:
        workitemparser.FeatsOrCaps("capabilities")
        common.Program()
        common.CapRoutine()
  
    #Portfolio Epics
    if "epics" in cfg.apiendpoint:
        workitemparser.FeatsOrCaps("epics")
        common.Program()
        common.EpicRoutine()   

    # Themes
    if "themes" in cfg.apiendpoint:
        workitemparser.FeatsOrCaps("themes")
        common.Program()
        common.ThemeRoutine()
        
####################################################################################################################################################################################       
if __name__ == "__main__":
    main()     
####################################################################################################################################################################################

