#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Exports data/configuration from a Jira Align instance to a JSON file,
    for backup or porting to another instance.
"""

import common
import cfg
import json

# Maximum number of records to return for main data items
MAX = 65500

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

    # Add the Jira Align Version Number - SSO blocks this
    #allConfigurationData['_version'] = cfg.jaVersion
    #print("Jira Align Version Number: " + cfg.jaVersion)
    
    # Collect all Region information and save it
    regionArray = common.ReadAllItems('regions', MAX)
    allConfigurationData['regions'] = regionArray
    print("A total of " + str(len(regionArray)) + " regions were retrieved from Jira Align")

    # Collect all the Jira Align Connector information and save it
    connectorJiraBoardArray = common.GetAllConnectorBoards()
    allConfigurationData['connectorJiraBoards'] = connectorJiraBoardArray
    print("A total of " + str(len(connectorJiraBoardArray)) + " Jira Boards were retrieved from Jira Align")

    connectorPrioritiesArray = common.GetAllConnectorPriorities()
    allConfigurationData['connectorPriorities'] = connectorPrioritiesArray
    print("A total of " + str(len(connectorPrioritiesArray)) + " Jira Priorities were retrieved from Jira Align")

    #connectorProductArray = common.GetAllConnectorProducts()
    #allConfigurationData['connectorProducts'] = connectorProductArray
    #print("A total of " + str(len(connectorProductArray)) + " Products were retrieved from Jira Align")

    connectorJiraProjectArray = common.GetAllConnectorProjects()
    allConfigurationData['connectorJiraProjects'] = connectorJiraProjectArray
    print("A total of " + str(len(connectorJiraProjectArray)) + " Jira Projects were retrieved from Jira Align")

    #connectorCustomFieldsArray = common.GetAllConnectorCustomFields()
    #allConfigurationData['connectorCustomFields'] = connectorCustomFieldsArray
    #print("A total of " + str(len(connectorCustomFieldsArray)) + " Custom Fields were retrieved from Jira Align")

    # Collect all Connector External Team Mapping information and save it
    connectorExternalTeamMappingArray = common.ReadAllItems('Connectors/2/TeamMappings', MAX)
    allConfigurationData['connectorExternalTeamMapping'] = connectorExternalTeamMappingArray
    print("A total of " + str(len(connectorExternalTeamMappingArray)) + " External Team Mappings were retrieved from Jira Align")

    # Collect all Country information and save it - not supported by V2 API
    #countryArray = common.ReadAllItems('countries', MAX)
    #allConfigurationData['countries'] = countryArray
    #print("A total of " + str(len(countryArray)) + " Countries were retrieved from Jira Align")

    # Collect all City information and save it
    cityArray = common.ReadAllItems('cities', MAX)
    allConfigurationData['cities'] = cityArray
    print("A total of " + str(len(cityArray)) + " Cities were retrieved from Jira Align")

    # Collect all Cost Center information and save it
    costCenterArray = common.ReadAllItems('CostCenters', MAX)
    allConfigurationData['costCenters'] = costCenterArray
    print("A total of " + str(len(costCenterArray)) + " Cost Centers were retrieved from Jira Align")

    # Collect all Division information and save it
    divisionArray = common.ReadAllItems('divisions', MAX)
    allConfigurationData['divisions'] = divisionArray
    print("A total of " + str(len(divisionArray)) + " Divisions were retrieved from Jira Align")

    # Collect all Domain information and save it
    domainArray = common.ReadAllItems('Domains', MAX)
    allConfigurationData['domains'] = domainArray
    print("A total of " + str(len(domainArray)) + " Domains were retrieved from Jira Align")
    # Domains/Health
    # DomainItemRelation

    # Collect all Grid Configurations for Capabilities information and save it
    gridConfigCapabilitiesArray = common.ReadAllItems('GridConfigurations/capability/ColumnConfigurations', MAX)
    allConfigurationData['GridConfigurationsCapabilities'] = gridConfigCapabilitiesArray
    print("A total of " + str(len(gridConfigCapabilitiesArray)) +\
          " Grid Configurations for Capabilities were retrieved from Jira Align")

    # Collect all Grid Configurations for Epics information and save it
    gridConfigEpicsArray = common.ReadAllItems('GridConfigurations/epic/ColumnConfigurations', MAX)
    allConfigurationData['GridConfigurationsEpics'] = gridConfigEpicsArray
    print("A total of " + str(len(gridConfigEpicsArray)) +\
          " Grid Configurations for Epics were retrieved from Jira Align")

    # Collect all Grid Configurations for Features information and save it
    gridConfigFeaturesArray = common.ReadAllItems('GridConfigurations/feature/ColumnConfigurations', MAX)
    allConfigurationData['GridConfigurationsFeatures'] = gridConfigFeaturesArray
    print("A total of " + str(len(gridConfigFeaturesArray)) +\
          " Grid Configurations for Features were retrieved from Jira Align")

    # Collect all Grid Configurations for Themes information and save it
    gridConfigThemesArray = common.ReadAllItems('GridConfigurations/theme/ColumnConfigurations', MAX)
    allConfigurationData['GridConfigurationsThemes'] = gridConfigThemesArray
    print("A total of " + str(len(gridConfigThemesArray)) +\
          " Grid Configurations for Themes were retrieved from Jira Align")

    # Collect all Grid Configurations for Dependencies information and save it
    gridConfigDependenciesArray = common.ReadAllItems('GridConfigurations/dependency/ColumnConfigurations', MAX)
    allConfigurationData['GridConfigurationsDependencies'] = gridConfigDependenciesArray
    print("A total of " + str(len(gridConfigDependenciesArray)) +\
          " Grid Configurations for Dependencies were retrieved from Jira Align")

    # Collect all Product information and save it
    productArray = common.ReadAllItems('products', MAX)
    allConfigurationData['products'] = productArray
    print("A total of " + str(len(productArray)) + " Products were retrieved from Jira Align")

    # Collect all Program information and save it
    programArray = common.ReadAllItems('programs', MAX)
    allConfigurationData['programs'] = programArray
    print("A total of " + str(len(programArray)) + " Programs were retrieved from Jira Align")

    # Collect all User information and save it
    userArray = common.ReadAllItems('users', MAX)
    allConfigurationData['users'] = userArray
    print("A total of " + str(len(userArray)) + " Users were retrieved from Jira Align")

    # Collect all Iteration information and save it
    iterationArray = common.ReadAllItems('iterations', MAX)
    allConfigurationData['iterations'] = iterationArray
    print("A total of " + str(len(iterationArray)) + " Iterations were retrieved from Jira Align")

    # Collect all Anchor Sprint information and save it
    anchorSprintArray = common.ReadAllItems('AnchorSprints', MAX)
    allConfigurationData['anchorsprints'] = anchorSprintArray
    print("A total of " + str(len(anchorSprintArray)) + " Anchor Sprints were retrieved from Jira Align")

    # Collect all Snapshot information and save it
    snapshotArray = common.ReadAllItems('snapshots', MAX)
    allConfigurationData['snapshots'] = snapshotArray
    print("A total of " + str(len(snapshotArray)) + " Strategic Snapshots were retrieved from Jira Align")

    # Collect all Theme information and save it
    themeArray = common.ReadAllItems('themes', MAX)
    allConfigurationData['themes'] = themeArray
    print("A total of " + str(len(themeArray)) + " Themes were retrieved from Jira Align")

    # Collect all Goal information and save it
    goalArray = common.ReadAllItems('goals', MAX)
    allConfigurationData['goals'] = goalArray
    print("A total of " + str(len(goalArray)) + " Goals were retrieved from Jira Align")

    # Collect all Release/PI information and save it
    releaseArray = common.ReadAllItems('releases', MAX)
    allConfigurationData['releases'] = releaseArray
    print("A total of " + str(len(releaseArray)) + " Releases were retrieved from Jira Align")

    # Collect all Customer information and save it
    customerArray = common.ReadAllItems('customers', MAX)
    allConfigurationData['customers'] = customerArray
    print("A total of " + str(len(customerArray)) + " Customers were retrieved from Jira Align")

    # Collect all Portfolio information and save it
    portfolioArray = common.ReadAllItems('portfolios', MAX)
    allConfigurationData['portfolio'] = portfolioArray
    print("A total of " + str(len(portfolioArray)) + " Portfolios were retrieved from Jira Align")

    # Collect all Idea information and save it
    ideaArray = common.ReadAllItems('ideas', MAX)
    allConfigurationData['ideas'] = ideaArray
    print("A total of " + str(len(ideaArray)) + " Ideas were retrieved from Jira Align")

    # Collect all Key Results information and save it
    keyResultsArray = common.ReadAllItems('keyresults', MAX)
    allConfigurationData['keyresults'] = keyResultsArray
    print("A total of " + str(len(keyResultsArray)) + " Key Results were retrieved from Jira Align")

    # Collect all Milestone information and save it
    milestoneArray = common.ReadAllItems('milestones', MAX)
    allConfigurationData['milestones'] = milestoneArray
    print("A total of " + str(len(milestoneArray)) + " Milestones were retrieved from Jira Align")

    # Collect all Release Vehicle information and save it
    releaseVehicleArray = common.ReadAllItems('releasevehicles', MAX)
    allConfigurationData['releasevehicle'] = releaseVehicleArray
    print("A total of " + str(len(releaseVehicleArray)) + " Release Vehicles were retrieved from Jira Align")

    # Collect all Teams information and save it
    teamsArray = common.ReadAllItems('teams', MAX)
    allConfigurationData['teams'] = teamsArray
    print("A total of " + str(len(teamsArray)) + " Teams were retrieved from Jira Align")

    # Collect all Risks information and save it
    risksArray = common.ReadAllItems('risks', MAX)
    allConfigurationData['risks'] = risksArray
    print("A total of " + str(len(risksArray)) + " Risks were retrieved from Jira Align")

    # Collect all Dependency information and save it
    dependencyArray = common.ReadAllItems('dependencies', MAX)
    allConfigurationData['dependency'] = dependencyArray
    print("A total of " + str(len(dependencyArray)) + " Dependencies were retrieved from Jira Align")

    # Collect all Custom Hierarchy information and save it
    customHierarchiesArray = common.ReadAllItems('CustomHierarchies', MAX)
    allConfigurationData['customhierarchies'] = customHierarchiesArray
    print("A total of " + str(len(customHierarchiesArray)) + " Custom Hierarchies were retrieved from Jira Align")

    # Save all configuration information in JSON format, pretty printed to be human readable and diffable
    configFileName = 'JiraAlign_config_data.json'
    print("Writing all Jira Align configuration data to: " + configFileName)
    with open(configFileName, 'w') as outfile:
        json.dump(allConfigurationData, outfile, indent=4, sort_keys=True)

    # Setup a single variable to contain all the item data
    allItemData = {}

    # Add the Jira Align Version Number
    allItemData['_version'] = cfg.jaVersion

    # Collect all Value Stream information and save it
    valueStreamArray = common.ReadAllItems('ValueStreams', MAX)
    allItemData['valuestreams'] = valueStreamArray
    print("A total of " + str(len(valueStreamArray)) + " Value Streams were retrieved from Jira Align")

    # Collect all Work Codes information and save it
    workCodesArray = common.ReadAllItems('WorkCodes', MAX)
    allItemData['workcodes'] = workCodesArray
    print("A total of " + str(len(workCodesArray)) + " Work Codes were retrieved from Jira Align")

    # Collect all Objective information and save it
    objectiveArray = common.ReadAllItems('objectives', MAX)
    allItemData['objectives'] = objectiveArray

    # Collect selected information about all JA Epics information and save it
    epicArray = common.ReadAllItems('epics', MAX)
    allItemData['epics'] = epicArray

    # Collect selected information about all JA Features information and save it
    featureArray = common.ReadAllItems('features', MAX)
    allItemData['features'] = featureArray

    # Collect selected information about all JA Capabilities information and save it
    capabilityArray = common.ReadAllItems('capabilities', MAX)
    allItemData['capabilities'] = capabilityArray

    # Collect selected information about all JA Stories information and save it
    storyArray = common.ReadAllItems('stories', MAX)
    allItemData['stories'] = storyArray

    # Collect selected information about all JA Defects information and save it
    defectsArray = common.ReadAllItems('defects', MAX)
    allItemData['defects'] = defectsArray

    # Collect selected information about all JA Task information and save it
    tasksArray = common.ReadAllItems('tasks', MAX)
    allItemData['tasks'] = tasksArray

    # Collect selected information about all JA Themes information and save it
    themeArray = common.ReadAllItems('themes', MAX)
    allItemData['themes'] = themeArray

    # Collect selected information about all JA Theme Groups information and save it
    themeGroupsArray = common.ReadAllItems('themegroups', MAX)
    allItemData['themegroups'] = themeGroupsArray

    # Save all configuration information in JSON format, pretty printed to be human readable and diffable
    with open('JiraAlign_config_data.json', 'w') as outfile:
        json.dump(allConfigurationData, outfile, indent=4, sort_keys=True)

    # Save all item information in JSON format, pretty printed to be human readable and diffable
    itemFileName = 'JiraAlign_item_data.json'
    print("Writing all item data to: " + itemFileName)
    with open(itemFileName, 'w') as outfile:
        json.dump(allItemData, outfile, indent=4, sort_keys=True)

    pass #eof

####################################################################################################################################################################################       
if __name__ == "__main__":
    main()     
####################################################################################################################################################################################
