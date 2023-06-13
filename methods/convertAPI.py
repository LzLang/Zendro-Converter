#   Imports
import os
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
def setup_hierarchy(input_path, output_path):
    """
    Walks through the input path and searches for json files.\n
    Also extracts the relative path to the json file for the output path.

    :param input_path: Path to the input hierarchy
    :param output_path: Path to the output hierarchy
    :return: Returns all found files in the input hierarchy
    """

    # All found files
    input_files = []
    # Relative paths to the files
    output_hierarchy = []

    # Walks through the input path
    for root, dir, files in os.walk(input_path):
        for filename in files:
            # Only json files are needed
            if '.json' in filename.lower():
                # Append the file
                input_files.append(os.path.join(root, filename))
                # Current / relative path to the file fpr output hierarchy
                current_path = root.replace(input_path+"\\", '')
                if not current_path in output_hierarchy:
                    output_hierarchy.append(current_path)

    # Call function to create output hierarchy
    create_output_hierarchy(output_path, output_hierarchy)

    return input_files


def create_output_hierarchy(output_path, hierarchy):
    """
    Creates the given hierarchy in the given path.

    :param output_path: Path for the hierarchy output
    :param hierarchy: Hierarchy that should be created
    """
    # For every directory in the hierarchy creates a directory
    for directory in hierarchy:
        path = os.path.join(output_path, directory)
        try:
            os.mkdir(path)
        # Directory already exists, log this
        except OSError as error:
            log(error)


def get_data(file_data):
    """
    From the passed data the properties are extracted.
    :param file_data: Data from a json file
    :return: Properties with a compatible type to Zendro
    """

    properties = file_data['properties']
    properties_data = {}
    for current_property in properties:
        property_type = get_type(properties[current_property]['type'])
        if property_type is None:
            continue
        if not 'description' in properties[current_property]:
            continue
        properties_data[current_property] = {
            'description': properties[current_property]['description'],
            'type': property_type
        }
    return properties_data


def get_type(types):
    """
    Checks if the passed type is Zendro compatible.

    :param types: Type of the property
    :return: Compatible type or none if not compatible
    """

    boolean_mask = np.nonzero(np.isin(ALLOWED_TYPES, types))[0]
    if len(boolean_mask):
        return ZENDRO_TYPES[ALLOWED_TYPES[boolean_mask[0]]]
    return None


def read_json(file):
    """
    Reads in a json file and returns its content.

    :param file: Path to the file JSON that should be read
    """

    try:
        # Open file and load json content
        with open(file, "r") as json_file:
            data = json.load(json_file)
            return data
    except OSError as error:
        log("Couldn't open file: " + file + "\tError: " + str(error))


def write_json(path, properties):
    """
    Writes the passed data to a json file.

    :param path: Path where the file should be saved (incl. filename)
    :param properties: Data that should be saved in json format
    """

    try:
        json_object = json.dumps(properties, indent=4)
        with open(path, "w") as file:
            file.write(json_object)
    except OSError as error:
        log("Couldn't open file: " + path + "\tError: " + str(error))


def log(msg):
    """
    Writes the message to a log-file.\n
    Logs the date and time automatically.

    :param msg: Message to log
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
