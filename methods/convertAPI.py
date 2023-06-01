#   Imports
import json
import numpy as np
from datetime import datetime, date
##############################


#   Constants / Types used in Zendro
ALLOWED_TYPES = ["string", "integer", "boolean"]
ZENDRO_TYPES = {
    'string': 'String',
    'integer': 'Int',
    'boolean': 'Boolean'
}
##############################


#   Functions
def log(msg):
    """Writes the message to a log-file.\n
    Logs the date and time automatically.\n
    Date - Time: msg
    """

    try:
        # Get current date and time and write this with the message to the log file
        with open("Log.txt", "a") as file:
            current_time = datetime.now().strftime("%H:%M:%S")
            file.write(str(date.today()) + " - " + current_time + ":\t" + msg + "\n")
    except OSError as error:
        # Prints the occurred error
        print(error)
        print("Not allowed to create or edit the log")


def read_json(file):
    """Reads in a json file and returns its content.\n
    Keyword arguments:\n
    - file: Path to the file JSON that should be read
    """

    try:
        # Open file and load json content
        with open(file, "r") as json_file:
            data = json.load(json_file)
            return data
    except OSError as error:
        log("Couldn't open file: " + file + "\tError: " + str(error))


def write_json(path, filename, properties):
    """Writes the passed data to a json file.\n
    Keyword arguments:\n
    - path: Path where the file should be saved\n
    - filename: Filename\n
    - property: Data that should be saved in json format
    """

    try:
        json_object = json.dumps(properties, indent=4)
        with open(path + filename, "w") as file:
            file.write(json_object)
    except OSError as error:
        log("Couldn't open file: " + path + filename + "\tError: " + str(error))


def get_type(types):
    """Checks if the passed type is Zendro compatible.\n
    - If compatible: return the type.\n
    - Else: return None.
    """

    boolean_mask = np.nonzero(np.isin(ALLOWED_TYPES, types))[0]
    if len(boolean_mask):
        return ZENDRO_TYPES[ALLOWED_TYPES[boolean_mask[0]]]
    return None


def get_data(file_data):
    """From the passed data the properties are extracted.\n
    Properties with a type that is compatible to Zendro, will be stored in propData.\n
    Returns propData, therefore only properties with compatible type.
    """

    properties = file_data['properties']
    properties_data = {}
    for current_property in properties:
        property_type = get_type(properties[current_property]['type'])
        if property_type is None:
            continue
        properties_data[current_property] = {
            'description': properties[current_property]['description'],
            'type': property_type
        }
    return properties_data
