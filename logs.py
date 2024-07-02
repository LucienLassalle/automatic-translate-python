import colorama
import datetime

def addLogs(logType, message):
    if(logType == "ERROR"):
        print(colorama.Fore.RED + f"[{logType}]" + colorama.Style.RESET_ALL + " : " + message)
    elif(logType == "WARNING"):
        print(colorama.Fore.YELLOW + f"[{logType}]" + colorama.Style.RESET_ALL + " : " + message)
    elif(logType == "INFO"):
        print(colorama.Fore.BLUE + f"[{logType}]" + colorama.Style.RESET_ALL + " : " + message)
    elif(logType == "OTHER"):
        print(colorama.Fore.GREEN + f"[{logType}]" + colorama.Style.RESET_ALL + " : " + message)

    with open('logs.txt', 'a', encoding='utf-8') as file:
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file.write(f"[{current_time}] [{logType}] : {message}\n")