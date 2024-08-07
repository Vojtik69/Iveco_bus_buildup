import os
import sys
import logging
from datetime import datetime
from loadConfig import paths

logPath = paths.get("log","")
if not logPath:
    home_dir = os.path.expanduser("~")
    logPath = os.path.join(home_dir, "Documents", "Altair", "iveco_log.log")

# Define global variables
LOGGER = None
FORMAT_STR = '%(asctime)s - %(levelname)s - %(message)s'
FILE_HANDLER = None
MAX_LINES = 4000


def SetupLogger():
    global LOGGER, FILE_HANDLER

    try:
        trim_log_file()
    except:
        pass

    LOGGER = logging.getLogger('my_logger')
    LOGGER.setLevel(logging.DEBUG)

    # Check if the log file exist and create it if necessary
    logDir = os.path.dirname(logPath)
    if not os.path.exists(logDir):
        os.makedirs(logDir)  # Create folder if missing
    if not os.path.exists(logPath):
        open(logPath, 'w').close()  # Create file if missing

    console_handler = logging.StreamHandler(sys.stdout)
    FILE_HANDLER = logging.FileHandler(logPath, encoding="utf-8")

    # Set levels for handlers
    console_handler.setLevel(logging.DEBUG)
    FILE_HANDLER.setLevel(logging.CRITICAL)

    # Create formatters and add them to handlers
    console_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_format = logging.Formatter(FORMAT_STR)

    console_handler.setFormatter(console_format)
    FILE_HANDLER.setFormatter(file_format)

    # Add handlers to the logger
    LOGGER.addHandler(console_handler)
    LOGGER.addHandler(FILE_HANDLER)

def trim_log_file():
    """ Ořízněte log soubor tak, aby obsahoval maximálně MAX_LINES řádků. """
    with open(logPath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    if len(lines) > MAX_LINES:
        with open(logPath, 'w', encoding='utf-8') as f:
            f.writelines(lines[-MAX_LINES:])

def getFormattedMessage(message):
    global LOGGER
    level_number = LOGGER.getEffectiveLevel()
    levelname = logging.getLevelName(level_number)
    name = LOGGER.name

    # Create a formatted message as per logger formatting
    formatted_message = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} - {levelname} - {message}"
    return formatted_message

def debug(message):
    global FILE_HANDLER
    logFile = FILE_HANDLER.baseFilename

    with open(logFile, 'a', encoding='utf-8') as f:
        formatMessage = getFormattedMessage(message)
        f.write(formatMessage + "\n")

SetupLogger()

