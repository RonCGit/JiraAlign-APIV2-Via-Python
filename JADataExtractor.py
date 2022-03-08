#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Exports data/configuration from a Jira Align instance to a JSON file,
    for backup or porting to another instance.
"""

import common
import cfg
import json

####################################################################################################################################################################################
def main():
####################################################################################################################################################################################
# MAIN
  
    # Call a subfile that helps handle shared routines and variables between this file and other files like workitemparser, jathemes, etc
    cfg.init()
    
    # Collect api server and endpoint. Also collect all of the instance json infomation we need into arrays with CollectUsrMenuItems
    common.CollectApiInfo()
 
    # Setup a single variable to contain all the configuration data
    allConfigurationData = {}

    # Collect all Region information and save it
    regionArray = common.GetAllRegions()
    allConfigurationData['regions'] = regionArray

    # Collect all Country information and save it - not supported via API V2
    #countryArray = common.GetAllCountries()
    #allConfigurationData['countries'] = countryArray

    # Collect all City information and save it
    cityArray = common.GetAllCities()
    allConfigurationData['cities'] = cityArray

    # Collect all Product information and save it
    productArray = common.GetAllProducts()
    allConfigurationData['products'] = productArray

    # Collect all Program information and save it
    programArray = common.GetAllPrograms()
    allConfigurationData['programs'] = programArray

    # Collect all User information and save it
    userArray = common.GetAllUsers()
    allConfigurationData['users'] = userArray

    # Collect all Iteration information and save it
    iterationArray = common.GetAllIterations()
    allConfigurationData['iterations'] = iterationArray

    # Collect all Snapshot information and save it
    snapshotArray = common.GetAllSnapshots()
    allConfigurationData['snapshots'] = snapshotArray

    # Collect all Theme information and save it
    themeArray = common.GetAllThemes()
    allConfigurationData['themes'] = themeArray

    # Collect all Goal information and save it
    goalArray = common.GetAllGoals()
    allConfigurationData['goals'] = goalArray

    # Collect all Objective information and save it
    objectiveArray = common.GetAllObjectives()
    allConfigurationData['objectives'] = objectiveArray

    # Collect all Release information and save it
    releaseArray = common.GetAllReleases()
    allConfigurationData['releases'] = releaseArray

    # Collect all Customer information and save it
    customerArray = common.GetAllCustomers()
    allConfigurationData['customers'] = customerArray

    # Collect all Portfolio information and save it
    portfolioArray = common.GetAllPortfolios()
    allConfigurationData['portfolio'] = portfolioArray

    # Collect all Idea information and save it
    ideaArray = common.GetAllIdeas()
    allConfigurationData['ideas'] = ideaArray

    # Collect all Key Results information and save it
    keyResultsArray = common.GetAllKeyResults()
    allConfigurationData['keyresults'] = keyResultsArray

    # Collect all Milestone information and save it
    milestoneArray = common.GetAllMilestones()
    allConfigurationData['milestones'] = milestoneArray

    # Collect all Release Vehicle information and save it
    releaseVehicleArray = common.GetAllReleaseVehicles()
    allConfigurationData['releasevehicle'] = releaseVehicleArray

    # Save all configuration information in JSON format, pretty printed to be human readable and diffable
    configFileName = 'JiraAlign_config_data.json'
    print("Writing all Jira Align configuration data to: " + configFileName)
    with open(configFileName, 'w') as outfile:
        json.dump(allConfigurationData, outfile, indent=4, sort_keys=True)

    # Setup a single variable to contain all the item data
    allItemData = {}

    # Collect selected information about all JA Epics information and save it
    epicArray = common.ReadAllItems('epics', 1000)
    allItemData['epics'] = epicArray

    # Collect selected information about all JA Features information and save it
    featureArray = common.ReadAllItems('features', 1000)
    allItemData['features'] = featureArray

    # Collect selected information about all JA Capabilities information and save it
    capabilityArray = common.ReadAllItems('capabilities', 1000)
    allItemData['capabilities'] = capabilityArray

    # Collect selected information about all JA Stories information and save it
    storyArray = common.ReadAllItems('stories', 1000)
    allItemData['stories'] = storyArray

    # Collect selected information about all JA Defects information and save it
    defectsArray = common.ReadAllItems('defects', 1000)
    allItemData['defects'] = defectsArray

    # Collect selected information about all JA Task information and save it
    tasksArray = common.ReadAllItems('tasks', 1000)
    allItemData['tasks'] = tasksArray

    # Save all configuration information in JSON format, pretty printed to be human readable and diffable
    with open('JiraAlign_config_data.json', 'w') as outfile:
        json.dump(allConfigurationData, outfile, indent=4, sort_keys=True)

    # Save all item information in JSON format, pretty printed to be human readable and diffable
    itemFileName = 'JiraAlign_item_data.json'
    print("Writing all item data to: " + itemFileName)
    with open(itemFileName, 'w') as outfile:
        json.dump(allItemData, outfile, indent=4, sort_keys=True)

####################################################################################################################################################################################       
if __name__ == "__main__":
    main()     
####################################################################################################################################################################################
