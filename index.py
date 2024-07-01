import requests
import translator
import json 
import colorama
import logs

configPath = "config.json"
try:
    with open(configPath, 'r', encoding='utf-8') as apiFile:
        config = json.load(apiFile)
        api_token = config.get('paratranz_api')
        if api_token is None:
            raise ValueError("paratranz_api key not found in config.json file.")
    
except FileNotFoundError:
    logs.addLogs("ERROR", "config.json file not found, script terminated.")
    exit(1)
except json.JSONDecodeError:
    logs.addLogs("ERROR", "Invalid config.json file, script terminated.")
    exit(1)
except ValueError:
    logs.addLogs("ERROR", "paratranz_api key not found in config.json file, script terminated.")
    exit(1)



def updateTranslate(result, translation):
    """
    Update the translation of the string in the Paratranz project.
    :param result: The string object to be updated
    :param translation: The translated text to be updated
    :return: True if the string is successfully updated, False otherwise
    """
    url = f"https://paratranz.cn/api/projects/{ParatranzProjectList[0]}/strings/{result.get('id')}"
    headers = {
        "Authorization": api_token,
        "Content-Type": "application/json"
    }
    data = {
        "translation": str(translation)
    }
    response = requests.put(url, headers=headers, json=data)
    if response.status_code == 200:
        logs.addLogs("INFO", f"String successfully translated for ID: {result.get('id')}")
        return True
    else:
        try:
            logs.addLogs("WARNING", f"Failed to update string for ID: {result.get('id')}, error {response.status_code}, {response.json()}")
        except:
            logs.addLogs("WARNING", f"Failed to update string for ID: {result.get('id')}, error {response}")


def getNbPages():
    """
    Get the total number of pages in the Paratranz project.
    :return: The total number of pages in the project
    """
    url = f"https://paratranz.cn/api/projects/{ParatranzProjectList[0]}/strings?pageCount=1&pageSize={DEFAULT_PAGE_SIZE}"
    headers = {
        "Authorization": api_token,
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    if(response.status_code == 200):
        strings =  response.json()
        results = strings.get('pageCount', [])
        return results
        
    else:
        try:
            logs.addLogs("ERROR", f"Error {response.status_code}: {response.json()}")
        except:
            logs.addLogs("ERROR", f"Error {response}")
        exit(1000)

def getStrings(number):
    """
    Get the strings from the Paratranz project.
    :param number: The page number to retrieve the strings
    :return: The list of strings in the page
    """
    url = f"https://paratranz.cn/api/projects/{ParatranzProjectList[0]}/strings?pageSize={DEFAULT_PAGE_SIZE}&page="+str(number)
    headers = {
        "Authorization": api_token,
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    if(response.status_code == 200):
        strings =  response.json()
        results = strings.get('results', [])
        return results
    else:
        try:
            logs.addLogs("ERROR", f"Error {response.status_code}: {response.json()}")
        except:
            logs.addLogs("ERROR", f"Error {response}")
        exit(1001)

def translateString(results):
    """
    Translate the strings in the Paratranz project.
    :param results: The list of strings to be translated
    """
    for result in results:
        if not result.get('translation'): 
            if (APIList[0] == "SYSTRAN"):
                frenchLine = translator.systranTranslate(result.get('original'))
            elif (APIList[0] == "DEEPL"):
                frenchLine = translator.deepLTranslate(result.get('original'))
            else: 
                frenchLine = translator.googleTranslate(result.get('original'))
            if frenchLine == False:
                logs.addLogs("WARNING", ">>> Problem with the API, changing...")
                APIList.pop(0)
                logs.addLogs("INFO", f"API changed to {APIList[0]}")
                translateString(results)
            else:
                try:
                    updateTranslate(result, frenchLine)
                except Exception as e:
                    logs.addLogs("ERROR", "Error updating the string." + str(e))


DEFAULT_PAGE_SIZE = 1

APIList = ["DEEPL", "GOOGLE"] # APIList = ["SYSTRAN", "DEEPL", "GOOGLE"]
ParatranzProjectList = [10733]

currentPage = 1
totalPage = -1
totalPage = int(getNbPages())
while currentPage <= totalPage:
    results = getStrings(currentPage)
    translateString(results)
    if(currentPage%100==0):
        logs.addLogs("INFO", f"Page {currentPage}/{totalPage} successfully translated.")
    currentPage += 1
