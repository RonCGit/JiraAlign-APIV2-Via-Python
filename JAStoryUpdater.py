#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Updates the PI and/or Description of all Stories that match the specified criteria
    entered by the user.  Helps with Jira Align data cleanup for work completed in
    the past.  Uses Jira Align PATCH calls with the Stories.
"""

from warnings import catch_warnings
import common
import cfg
import json

# Maximum number of records to return for main data items
MAX = 1000

def replace_non_ascii_with_spaces(text):
    """
    Scans a string and replaces all characters outside of standard ASCII (0-127) with spaces.

    Parameters:
    text (str): The input string to be processed.

    Returns:
    str: The processed string with non-ASCII characters replaced by spaces.
    """
    return ''.join([char if ord(char) < 128 else ' ' for char in text])

def replace_non_ascii_and_newlines_with_spaces(text):
    """
    Scans a string and replaces all characters outside of standard ASCII (0-127), 
    carriage returns (\r), and new line characters (\n) with spaces.

    Parameters:
    text (str): The input string to be processed.

    Returns:
    str: The processed string with non-ASCII characters, carriage returns, and new line characters replaced by spaces.
    """
    return ''.join([' ' if ord(char) >= 128 or char in ['\r', '\n'] else char for char in text])

def get_key_info(dataArray, id):
    """
    Scans the given array of objects, looking for the one with the given id, and return
    key information about it.
    
    Parameters:
    dataArray: Array of objects to scan
    id: ID number to look for
    
    Returns:
    str: The ID number and the descriptive name/title of it, if found.  An empty string
    is returned if it is not found.
    
    This function assumes that the given array has a field called 'id' in it.
    """
    tmpStr = ""
    for item in dataArray:
        if (item['id'] == id):
            tmpStr = str(item['id'])
            if 'title' in item:
                tmpStr = tmpStr + "/" + item['title']
    return tmpStr
                                                                                                         
####################################################################################################################################################################################
def main():
####################################################################################################################################################################################
# MAIN
  
    # Call a subfile that helps handle shared routines and variables between this file and other files like workitemparser, jathemes, etc
    cfg.init()
    
    # Collect api server and endpoint. Also collect all of the instance json infomation we need into arrays with CollectUsrMenuItems
    common.CollectApiInfo()
 
    print("Jira Align Version Number: " + cfg.jaVersion)

    # Collect all Program information and save it
    programArray = common.ReadAllItems('programs', MAX)
    print("A total of " + str(len(programArray)) + " Programs were retrieved from Jira Align")

    # Collect all Release/PI information and save it
    releaseArray = common.ReadAllItems('releases', MAX)
    print("A total of " + str(len(releaseArray)) + " Releases/PIs were retrieved from Jira Align")

    # Gather info from the user
    print("")
    programId = int(input("Enter the Jira Align Program ID to search in: "))
    stateId = int(input("Enter the Jira Align State ID to search for (5 is Accepted): "))
    newPIID = int(input("Enter the NEW Jira Align PI ID (JA Release) to use: "))
    
    # Hardcoded data for testing
    #programId = 0
    #stateId = 5 # Accepted
    #newPIID = 0 # 

    # Print out the name of the Program so it can be visually verified
    print("")
    print("Verify these are correct:")
    print(" Program to search in: " + get_key_info(programArray, programId))
    print(" PI to set Stories to: " + get_key_info(releaseArray, newPIID))
    print("")

    # Collect selected information about all JA Stories information and save it
    storyArray = common.ReadAllItems('stories', MAX, programId)

    skippedStoryCount = 0
    successfulChangeCount = 0
    failedChangeCount = 0
    batch = True
    matchFor2023Count = 0
    
    # Loop through all the stories, looking for ones in the Unassigned Backlog,
    # that match the requested ProgramId and stateId.
    print("Searching through the stories...")  
    for aStory in storyArray:
        # If this story is assigned to a PI, then skip it
        if 'releaseId' in aStory:
            skippedStoryCount = skippedStoryCount + 1
            continue
        # Else this story is NOT assigned to a PI (it's in the Unassigned Backlog)
        else:
            # If the Program matches what we are looking for
            if aStory['programId'] == programId:
                # If the State of the story matches what we are looking for
                if aStory['state'] == stateId:
                    tmpStr = ""
                    print("")
                    tmpStr = tmpStr + "STORY: ID=" + str(aStory['id']) +\
                        " State=" + str(aStory['state'])
                    if 'externalKey' in aStory:
                        tmpStr = tmpStr + " JIRA Key=" + aStory['externalKey']
                    tmpStr = tmpStr +\
                          " Accepted Date=" + aStory['acceptedDate'] +\
                          " Title=" + aStory['title']
                    print(tmpStr)
                    
                    # Count of Stories accepted in 2023
                    if ("2023-" in aStory['acceptedDate']):
                        matchFor2023Count = matchFor2023Count + 1
                        
                    # Only prompt for stories accepted in 2021 or 2022
                    if ("2021-" not in aStory['acceptedDate']) and ("2022-" not in aStory['acceptedDate']):
                        print("  Not accepted in 2021/2022, skipping")
                        skippedStoryCount = skippedStoryCount + 1
                        continue
                    
                    # If we are NOT in batch mode, then confirm before moving the story
                    if (batch != True):
                        # Confirm that we want to move this story
                        moveStory = input("DO YOU WANT TO MOVE THIS STORY? ")
                        if (moveStory != 'y'):
                            continue
                    else:
                        print("  Attempting to move the story...")
                    
                        header = {'Content-Type': 'application/json;odata.metadata=minimal;odata.streaming=true'}

                        # If the Description is missing, use the Title in it's place for
                        # that PATCH so that it will work (since Description is a required
                        # field in Jira Align).
                        if ('description' not in aStory):
                            # Create the PATCH data    
                            body = [{'value': 'foo', 'path': '/description','op': 'replace'}]
                            body[0]['value'] = aStory['title']
                            # Update the Story's Description in Jira Align with a PATCH
                            response = common.PatchToJiraAlign(header, body, True, True, 
                                                               cfg.instanceurl + "/Stories/" + str(aStory['id']))
                            if (response.status_code == 204):
                                # Create the PATCH data    
                                body = [{'value': 193, 'path': '/releaseId','op': 'replace'}] # 193 = placeholder number
                                body[0]['value'] = newPIID # update the placeholder
                            
                                # Update the Story in Jira Align with a PATCH
                                response = common.PatchToJiraAlign(header, body, True, True, 
                                                                   cfg.instanceurl + "/Stories/" + str(aStory['id']))
                                if (response.status_code == 204):
                                    print("  Story successfully updated in Jira Align.")
                                    successfulChangeCount = successfulChangeCount + 1
                                else:
                                    print(response)
                                    failedChangeCount = failedChangeCount + 1
                                    foo = input("FAILURE")
                            else:
                                print("Description could not be updated, skipping this Story")
                                failedChangeCount = failedChangeCount + 1
                else:
                    skippedStoryCount = skippedStoryCount + 1
            else:
                skippedStoryCount = skippedStoryCount + 1

    # Output operation summary
    print("")                    
    print(str(skippedStoryCount) + " Stories were skipped")
    print(str(successfulChangeCount) + " Stories were successfully changed")
    print(str(failedChangeCount) + " Stories failed to be changed")
    print(str(matchFor2023Count) + " Stories Accepted in 2023")
                
    pass #eof

####################################################################################################################################################################################       
if __name__ == "__main__":
    main()     
####################################################################################################################################################################################
