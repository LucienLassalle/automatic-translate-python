import requests
import translator
import json 
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

def translateString(results, googleTranslate, argosTranslate, deeplTranslate, systranTranslate):
    """
    Translate the strings in the Paratranz project.
    :param results: The list of strings to be translated
    """
    for result in results:
        if not result.get('translation'): 
            listTranslate = []
            listIA = []
            listTranslate.append(result.get('original'))
            listIA.append("ORIGINAL : ")
            if (type(googleTranslate) != bool):
                googleTranslate = translator.googleTranslate(result.get('original'))
            if (type(googleTranslate) != bool):
                listTranslate.append(googleTranslate)
                listIA.append("GOOGLE TRANSLATE : ")
            
            if (type(argosTranslate) != bool):
                argosTranslate = translator.argosTranslate(result.get('original'))
            if (type(argosTranslate) != bool):
                listTranslate.append(argosTranslate)
                listIA.append("ARGOS TRANSLATE : ")

            if (type(deeplTranslate) != bool):
                deeplTranslate = translator.deepLTranslate(result.get('original'))
            if (type(deeplTranslate) != bool):
                listTranslate.append(deeplTranslate)
                listIA.append("DEEPL TRANSLATE : ")
            
            if (type(systranTranslate) != bool):
                systranTranslate = translator.systranTranslate(result.get('original'))
            if (type(systranTranslate) != bool):
                listTranslate.append(systranTranslate)
                listIA.append("SYSTRAN TRANSLATE : ")

            if (len(listTranslate) == 1):
                logs.addLogs("ERROR", ">>> No API available, skipping...")
                exit(0)
            else:
                if (len(listTranslate)>2 and all(x == listTranslate[0] for x in listTranslate[1:])):
                    try:
                        updateTranslate(result, googleTranslate)
                    except Exception as e:
                        logs.addLogs("ERROR", f"Failed to update string for ID: {result.get('id')}, error {e}")
                else:
                    logs.addLogs("OTHER", ">>> Only one translation API is not enough, or the translation between multiple APIs is incorrect.")
                    lastTranslate = translator.hugchatTranslate(listIA, listTranslate)
                    if (type(lastTranslate) != bool):
                        try:
                            updateTranslate(result, lastTranslate)    
                        except Exception as e:
                            logs.addLogs("ERROR", f"Failed to update string for ID: {result.get('id')}, error {e}")
                    else:
                        logs.addLogs("ERROR", ">>> The AI-based API failed to provide a correct response, therefore it is not possible to send the translation.")
    return "", argosTranslate, deeplTranslate, systranTranslate # googleTranslate, argosTranslate, deeplTranslate, systranTranslate


DEFAULT_PAGE_SIZE = 1
DEBUG_MODE = int(input("Do you want to open the debug mode ? (1/0) : "))


ParatranzProjectList = [10733]


currentPage = 1
totalPage = -1
totalPage = int(getNbPages())
if DEBUG_MODE == 1:
    results = getStrings(currentPage)
    googleTranslate = ""
    argosTranslate = ""
    deeplTranslate = ""
    systranTranslate = ""
    translateString(results, googleTranslate, argosTranslate, deeplTranslate, systranTranslate)
    for result in results:
        original = result.get('original')
        print("DEBUG ORIGINAL \n" + original)
        gTranslate = translator.googleTranslate(original)
        argrosTranslate = translator.argosTranslate(original)
        deeplTranslate = translator.deepLTranslate(original)
        systranTranslate = translator.systranTranslate(original)
        print("DEBUG GOOGLE TRANSLATE \n" + str(gTranslate))
        print("DEBUG ARGOS TRANSLATE \n" + str(argrosTranslate))
        print("DEBUG DEEPL TRANSLATE \n" + str(deeplTranslate))
        print("DEBUG SYSTRAN TRANSLATE \n" + str(systranTranslate))
        listTranslate = []
        listIA = []
        listTranslate.append(original)
        listIA.append("ORIGINAL : ")
        if(type(gTranslate) != bool):
            listTranslate.append(gTranslate)
            listIA.append("GOOGLE TRANSLATE : ")
        if(type(argrosTranslate) != bool):
            listTranslate.append(argrosTranslate)
            listIA.append("ARGOS TRANSLATE : ")
        if(type(deeplTranslate) != bool):
            listTranslate.append(deeplTranslate)
            listIA.append("DEEPL TRANSLATE : ")
        if(type(systranTranslate) != bool):
            listTranslate.append(systranTranslate)
            listIA.append("SYSTRAN TRANSLATE : ")
        if (len(listTranslate) == 1):
            logs.addLogs("ERROR", ">>> No API available, skipping...")
            exit(0)
        
        if (len(listTranslate)>2 and all(x == listTranslate[0] for x in listTranslate[1:])):
            try:
                updateTranslate(result, gTranslate)
            except Exception as e:
                logs.addLogs("ERROR", f"Failed to update string for ID: {result.get('id')}, error {e}")
        else:
            lastTranslate = translator.hugchatTranslate(listIA, listTranslate)
            logs.addLogs("OTHER", ">>> Only one translation API is not enough, or the translation between multiple APIs is incorrect.")
            print("DEBUG LAST TRANSLATE \n" + lastTranslate)
        print("DEBUG END \n")

else:
    gTranslate = ""
    argosTranslate = ""
    deeplTranslate = ""
    systranTranslate = ""
    while currentPage <= totalPage:
        results = getStrings(currentPage)
        gTranslate, argosTranslate, deeplTranslate, systranTranslate = translateString(results, gTranslate, argosTranslate, deeplTranslate, systranTranslate)
        if(currentPage%100==0):
            logs.addLogs("INFO", f"Page {currentPage}/{totalPage} successfully translated.")
        currentPage += 1
    