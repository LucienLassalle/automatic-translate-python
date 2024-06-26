import json
from googletrans import Translator
import sys
import re

sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')

def logs(level, message):
    print(f"LEVEL : [{level}] = {message}")

inputPath = "english/English.json"
outputPath = "french/French.json"
configPath = "config.json"

translator = Translator()
try:
    with open(configPath, 'r', encoding='utf-8') as apiFile:
        config = json.load(apiFile)
        api_key = config.get('api_key')
        api_pwd = config.get('api_pwd')
        api_url = config.get('api_url')
        if api_key is None or api_pwd is None or api_url is None:
            raise ValueError("Une ou plusieurs clés de configuration manquent dans le fichier config.json.")
except FileNotFoundError:
    logs("GRAVE", "Fichier introuvable, fin du script.")
    exit(1)
except json.JSONDecodeError:
    logs("GRAVE", "Fichier config.json invalide, fin du script.")
    exit(1)
except ValueError:
    logs("GRAVE", "Une ou plusieurs clés de configuration manquent dans le fichier config, fin du script")
    exit(1)

compteur = 0
with open(inputPath, 'r', encoding='utf-8') as inputFile:
    english = json.load(inputFile)

    translateFrench = {}
    total_lines = len(english)
    
    for index, line in enumerate(english, start=1):
        try:
            exceptWords = re.findall(r'\{\{(.*?)\}\}', line)
            lineEscaped = line
            for index2, word in enumerate(exceptWords, start=1):
                lineEscaped = lineEscaped.replace(word, str(index2)+"mot")

            frenchLine = translator.translate(lineEscaped, src='en', dest='fr').text

            for index2, word in enumerate(exceptWords, start=1):
                frenchLine = frenchLine.replace(str(index2)+"mot", word)
                frenchLine = frenchLine.replace(str(index2)+"Mot", word)
            
            translateFrench[f"{line}"] = f"{frenchLine}"
            compteur += 1
            remaining_lines = total_lines - compteur
            if(compteur % 100 == 0):
                print(f"Lignes traduites : {compteur} / Lignes restantes : {remaining_lines}")
                # with open(outputPath, "w", encoding='utf-8') as outputFile:
                #     json.dump(translateFrench, outputFile, ensure_ascii=False, indent=4)
                # exit(6)
        except Exception as e:
            print(f"Erreur lors de la traduction : {str(e)}")
            # En cas d'erreur, ajouter la ligne originale avec une clé unique
            translateFrench[f"{line}"] = line
    
    with open(outputPath, "w", encoding='utf-8') as outputFile:
        json.dump(translateFrench, outputFile, ensure_ascii=False, indent=4)

print(f"Traduction terminée. Total des lignes traduites : {compteur}")
