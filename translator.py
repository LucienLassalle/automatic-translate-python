import json
import requests
from googletrans import Translator
import deepl
import re
import logs

configPath = "config.json"

def googleTranslate(text, src="en", dest="fr"):
    """
    Translates the given text from the source language to the destination language using the Google Translate API.
    :param text: Text to be translated
    :param src: Source language of the text
    :param dest: Destination language of the text
    :return: Translated text
    """
    translator = Translator()
    
    exceptWords = re.findall(r'\{\{(.*?)\}\}', text)
    lineEscaped = text
    if(len(exceptWords) != 0):
        for index2, word in enumerate(exceptWords, start=1):
            lineEscaped = lineEscaped.replace(word, str(index2)+"mot")

    try:
        outputLine = translator.translate(lineEscaped, src=src, dest=dest).text
    except Exception as e:
        outputLine = text

    # Replace the exceptWords back to their original form
    if(len(exceptWords) != 0):
        for index2, word in enumerate(exceptWords, start=1):
            outputLine = outputLine.replace(str(index2)+"mot", word)
            outputLine = outputLine.replace(str(index2)+"Mot", word)
            outputLine = outputLine.replace(str(index2)+"MOT", word)
            outputLine = outputLine.replace(str(index2)+" mot", word)
            outputLine = outputLine.replace(str(index2)+" Mot", word)
            outputLine = outputLine.replace(str(index2)+" MOT", word)
        
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
    with open(configPath, 'r', encoding='utf-8') as apiFile:
        config = json.load(apiFile)
        systran_key = config["systran_key"]
    
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