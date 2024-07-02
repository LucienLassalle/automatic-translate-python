import json
import requests
from googletrans import Translator
import deepl
import re
import logs
from hugchat import hugchat
from hugchat.login import Login

configPath = "config.json"

def hugchatTranslate(listIA, listText, src="en", dest="fr"):
    cookie_path_dir = "./cookies/" # NOTE: trailing slash (/) is required to avoid errors
    with open(configPath, 'r', encoding='utf-8') as apiFile:
        config = json.load(apiFile)
        EMAIL = config["EMAIL_API_HUGCHAT"]
        PASSWORD = config["PASSWORD_API_HUGCHAT"]
        GENERIQUE = config["MESSAGE_GENERIQUE"]

    sign = Login(EMAIL, PASSWORD)
    cookies = sign.login(cookie_dir_path=cookie_path_dir, save_cookies=False)

    # Create your ChatBot
    chatbot = hugchat.ChatBot(cookies=cookies.get_dict())  # or cookie_path="usercookies/<email>.json"

    original = listIA[0] + listText[0]
    translated = " ".join(listIA[1:]) + " ".join(listText[1:])

    translated = GENERIQUE + "\n" + original + "\n" + translated
    query_result = chatbot.query(translated, web_search=True)
    return query_result


def googleTranslate(text, src="en", dest="fr"):
    """
    Translates the given text from the source language to the destination language using the Google Translate API.
    :param text: Text to be translated
    :param src: Source language of the text
    :param dest: Destination language of the text
    :return: Translated text
    """
    translator = Translator()

    # Find words to be excluded from translation
    exceptWords = re.findall(r'\{\{(.*?)\}\}', text)
    lineEscaped = text

    # Replace words to be excluded with placeholders
    if exceptWords:
        for index, word in enumerate(exceptWords, start=1):
            lineEscaped = lineEscaped.replace(f'{{{{{word}}}}}', f'{index}mot')

    try:
        translated = translator.translate(lineEscaped, src=src, dest=dest)
        outputLine = translated.text
    except Exception as e:
        print(f'Error during translation: {str(e)}')
        exit(500)
        outputLine = text

    # Replace placeholders with the original words
    if exceptWords:
        for index, word in enumerate(exceptWords, start=1):
            outputLine = re.sub(f'{index}mot', word, outputLine, flags=re.IGNORECASE)

    return outputLine



def deepLTranslate(text, src="en", dest="fr"):
    """
    Translates the given text from the source language to the destination language using the DeepL API.
    :param text: Text to be translated
    :param src: Source language of the text
    :param dest: Destination language of the text
    :return: Translated text
    """
    # Load API configuration from config.json
    with open(configPath, 'r', encoding='utf-8') as apiFile:
        config = json.load(apiFile)
        deepl_key = config["deepl_key"]
    
    translator = deepl.Translator(deepl_key)
    exceptWords = re.findall(r'\{\{(.*?)\}\}', text)
    lineEscaped = text
    if(len(exceptWords) != 0):
        for index2, word in enumerate(exceptWords, start=1):
            lineEscaped = lineEscaped.replace(word, str(index2)+"mot")

    try:
        outputLine = str(translator.translate_text(text, source_lang=src, target_lang=dest))
    except Exception as e:
        if("Quota" in str(e)):
            return False
        outputLine = text
    
    if(len(exceptWords) != 0):
        for index2, word in enumerate(exceptWords, start=1):
            outputLine = outputLine.replace(str(index2)+"mot", word)
            outputLine = outputLine.replace(str(index2)+"Mot", word)
            outputLine = outputLine.replace(str(index2)+"MOT", word)
            outputLine = outputLine.replace(str(index2)+" mot", word)
            outputLine = outputLine.replace(str(index2)+" Mot", word)
            outputLine = outputLine.replace(str(index2)+" MOT", word)
        
    return outputLine





def systranTranslate(text, src="en", dest="fr"):
    """
    Translates the given text from the source language to the destination language using the Systran API.
    :param text: Text to be translated
    :param src: Source language of the text
    :param dest: Destination language of the text
    :return: Translated text
    """
    # Load API configuration from config.json
    try:
        with open(configPath, 'r', encoding='utf-8') as apiFile:
            config = json.load(apiFile)
            systran_key = config["systran_key"]
    except FileNotFoundError:
        logs.addLogs("ERROR", "config.json file not found, script terminated.")
        exit(1)
    except json.JSONDecodeError:
        logs.addLogs("ERROR", "Invalid config.json file, script terminated.")
        exit(1)
    except KeyError:
        logs.addLogs("ERROR", "systran_key key not found in config.json file, script terminated.")
        exit(1)
    except Exception as e:
        logs.addLogs("ERROR", f"Error: {e}")
        exit(1)
    # Prepare request payload
    payload = {
        "input": [text], 
        "source": src,
        "target": dest
    }
    
    # Send translation request to Systran API
    headers = {
        "Accept": "application/json",
        "Authorization": f"Key {systran_key}"
    }
    response = requests.post("https://api-platform.systran.net/translation/text/translate", json=payload, headers=headers)
    
    # Check if translation is successful
    if response.status_code != 200:
        try:
            logs.addLogs("WARNING", f"Systran API malfunction: {response.status_code}")
        except:
            logs.addLogs("WARNING", f"Systran API malfunction: {response}")
        return False
    
    # Parse and return the translated text from the response
    translated_text = response.json()["outputs"][0]["output"]
    return translated_text