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
            if os.path.splitext(filename)[1].lower() == '.json':
                # Append the file
                input_files.append(os.path.join(root, filename))
                # Current / relative path to the file fpr output hierarchy
                current_path = os.path.basename(root)
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


def get_type(file_data):
    """
    Checks the passed data for a Zendro compatible type and returns it
    :param file_data: Data from a json file (a dictionary)
    :return: Returns Zendro compatible type or none
    """

    # walk through the items of the dictionary
    for key, value in file_data.items():
        if key.lower() == 'type':
            # if the properties has no compatible type it is not needed therefore None is returned
            boolean_mask = np.nonzero(np.isin(ALLOWED_TYPES, value))[0]
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
            data = json.load(json_file)['properties']
            return data
    except OSError as error:
        log("Couldn't open file: " + file + "\tError: " + str(error))


def write_json(path, properties, args):
    """
    Writes the passed data to a json file.

    :param path: Path where the file should be saved (incl. filename)
    :param properties: Data that should be saved in json format
    """

    try:
        # Der Plan ist eine neue Variable zu machen, die dann wie auf Github die Sachen macht
        model = {
            'model': os.path.splitext(os.path.basename(path))[0],
            'storageType': args.storage_type,
            'attributes': properties
        }
        json_object = json.dumps(model, indent=4)
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
            file.write(f"{str(date.today())} - {current_time}:\t{msg}\n")
    except OSError as error:
        # Prints the occurred error
        print(error)
        print("Not allowed to create or edit the log")
