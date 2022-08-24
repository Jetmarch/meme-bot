from enum import Enum
import datetime

'''
Взято из вопроса https://stackoverflow.com/questions/287871/how-do-i-print-colored-text-to-the-terminal
'''
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    DEBUG = '\033[90m'

    RED_BG = '\033[41m'

class LogType(Enum):
    OK = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4
    DEBUG = 5

class Log:

    @staticmethod
    def log(type: LogType, *args) -> None:
        log_text = str(datetime.datetime.now())
        if(type == LogType.OK):
            log_text += f" {bcolors.OKGREEN}[OK]      {bcolors.ENDC} "
        elif(type == LogType.INFO):
            log_text += f" {bcolors.OKBLUE}[INFO]    {bcolors.ENDC} "
        elif(type == LogType.WARNING):
            log_text += f" {bcolors.WARNING}[WARNING] {bcolors.ENDC} "
        elif(type == LogType.ERROR):
            log_text += f" {bcolors.FAIL}[ERROR]   {bcolors.ENDC} "
        elif(type == LogType.CRITICAL):
            log_text += f" {bcolors.BOLD + bcolors.RED_BG}[CRITICAL]{bcolors.ENDC} "
        elif(type == LogType.DEBUG):
            log_text += f" {bcolors.DEBUG}[DEBUG]   {bcolors.ENDC} "

        for arg in args:
            log_text += str(arg) + " "
        print(log_text)