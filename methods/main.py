import os
import sys
import json
import argparse
from datetime import datetime, date
from pathlib import Path

##############################


BrAPI_TYPES = ["string", "integer", "boolean", "number"]
ZENDRO_TYPES = {
    'string': 'String',
    'integer': 'Int',
    'boolean': 'Boolean',
    'number': 'Float'
}

##############################


# Create parser for command-line options
parser = argparse.ArgumentParser(
    prog='Converter',
    description='Converts BrAPI json-schemas to a Zendro data model'
)

parser.add_argument('-i', '--input-path',
                    help='Path to the BrAPI schemas.',
                    required=True)

parser.add_argument('-o', '--output-path',
                    help='Path where the Zendro data models should be stored.',
                    required=True)

# Define a storage type
parser.add_argument('-s', '--storage-type',
                    help='Type of storage where the model is stored.',
                    choices=['sql', 'generic', 'zendro-server', 'cassandra', 'mongodb', 'neo4j',
                             'presto/trino', 'amazon-s3', 'distributed-data-model', 'adapter'],
                    default='sql')

# Define a primary key
parser.add_argument('-p', '--primary-key-name',
                    help='Name of the primary key.')

# Define the type of the primary key
parser.add_argument('-t', '--primary-key-type',
                    help='Type of the primary key.',
                    choices=['Int', 'String'],
                    default='String')

# Parse arguments
args = parser.parse_args()


##############################


def main():
    """
    Main function of this program.\n
    You only need to call this function.
    """
    # Search for json files and extract the models to a variable
    input_models = get_models(get_files(args.input_path))

    # Extract properties from all models
    output_models = {}
    for model in input_models:
        output_models[model] = get_properties(input_models[model]["properties"], model)

    # Write the Zendro data model definitions
    write_json(output_models)


def get_files(input_path):
    """
    Walks through the input path and searches for json files.\n
    Also extracts the relative path to the json file for the output path.

    :param input_path: Path to the input files/directories
    :return: Returns all found files in the input hierarchy
    """

    # All found files
    input_files = []

    # Walks through the input path
    for root, directories, files in os.walk(input_path):
        for filename in files:
            # Only json files are needed
            if os.path.splitext(filename)[1].lower() == '.json':
                # Append the file
                file_path = os.path.join(root, filename)
                input_files.append(file_path)

    return input_files


def get_models(input_files):
    """
    Read in the given files and extract all models from it.\n
    Get a formatted dictionary of data models included in those files.

    :param input_files: List of files to extract models from
    :return: Formatted dictionary of data models
    """
    try:
        files_data = {}
        for file in input_files:
            with open(file, "r") as open_file:
                models = json.load(open_file)['$defs']
                for current_model in models:
                    files_data[current_model] = {}
                    files_data[current_model]['properties'] = models[current_model]['properties']
                    files_data[current_model]['required'] = models[current_model]['required']

        return files_data if files_data else None

    except OSError as file_error:
        log(f"Couldn't open files: {file_error}")
    except Exception as model_exception:
        print(model_exception)
        log(f"An error occurred: {model_exception}")
        sys.exit(1)


def get_properties(input_model_properties, current_model):
    """
    Get a formatted dictionary of data models with Zendro compatible data types and references.\n
    Ready to be writen in json format.

    :param input_model_properties: Dictionary of all properties included in the current model
    :param current_model: The name of the current model
    :return: Formatted dictionary of data models compatible to Zendro
    """

    model_properties = {
        "attributes": {},
        "associations": {},
        "primary_key": {}
    }
    foreign_keys = {}

    for model_property in input_model_properties:
        current_property = input_model_properties[model_property]

        if "relationshipType" not in current_property:
            property_type = get_property_type(current_property)

            if model_property == f"{current_model[0].lower() + current_model[1:]}DbId":
                model_property = args.primary_key_name if args.primary_key_name else model_property

                model_properties["primary_key"] = {
                    "Name": model_property,
                    "Type": f"[ {args.primary_key_type} ]"
                }

                property_type = f"[ {args.primary_key_type} ]"

            if property_type:
                description = ""
                if "description" in current_property:
                    description = current_property['description'].replace("'", "\'")
                    description.replace('"', "\"")
                model_properties["attributes"][model_property] = {
                    "type": property_type,
                    "description": description
                }
            else:
                continue
        else:
            association_relationship_type = current_property["relationshipType"].replace("-", "_")

            if "items" in current_property:
                association_target = current_property["items"]["$ref"].split("/")[-1]
            else:
                association_target = current_property["$ref"].split("/")[-1]

            match association_relationship_type:
                case "many_to_one":
                    target_key = f"{current_property["referencedAttribute"]}_IDs"
                    source_key = f"{model_property}_ID"
                    foreign_keys[source_key] = "String"
                case "one_to_many":
                    target_key = f"{current_property["referencedAttribute"]}_ID"
                    source_key = f"{model_property}_IDs"
                    foreign_keys[source_key] = "[ String ]"
                case "many_to_many":
                    target_key = f"{current_property["referencedAttribute"]}_IDs"
                    source_key = f"{model_property}_IDs"
                    foreign_keys[source_key] = "[ String ]"
                case "one_to_one":
                    target_key = f"{current_property["referencedAttribute"]}_ID"
                    source_key = f"{model_property}_ID"
                    foreign_keys[source_key] = "String"
                case _:
                    log(f"Model: {current_model}\tProperty: {model_property}\t !Wrong association type!")
                    continue

            model_properties["associations"][model_property] = {
                "type": association_relationship_type,
                "implementation": "foreignkeys",
                "reverseAssociation": current_property["referencedAttribute"],
                "target": association_target,
                "targetKey": target_key,
                "sourceKey": source_key,
                "keysIn": current_model,
                "targetStorageType": args.storage_type
            }

        model_properties["attributes"].update(foreign_keys)
    return model_properties


def get_property_type(input_property):
    """
    Checks the passed item for a Zendro compatible type and returns it
    :param input_property: An item from a json file (a dictionary)
    :return: Returns Zendro compatible type or none
    """

    property_type = None
    if 'type' in input_property:
        # if the properties has no compatible type it is not needed therefore None is returned
        if isinstance(input_property['type'], list):
            for item_type in input_property['type']:
                if item_type == "array":
                    if input_property["items"]["type"] == "array":
                        property_type = f"[ {ZENDRO_TYPES[input_property["items"]["items"]["type"]]} ]"
                    else:
                        property_type = f"[ {ZENDRO_TYPES[input_property["items"]["type"]]} ]"
                if item_type in BrAPI_TYPES:
                    property_type = ZENDRO_TYPES[item_type]
        else:
            if input_property['type'] in BrAPI_TYPES:
                property_type = ZENDRO_TYPES[input_property['type']]

    return property_type


def write_json(output_models):
    """
    Writes the passed models to their own json file.

    :param output_models: Dictionary with model definitions compatible to Zendro
    :return: None: Nothing is returned
    """
    try:
        for model in output_models:
            json_file = {
                "model": model,
                "storageType": args.storage_type,
                "attributes": output_models[model]["attributes"],
                "associations": output_models[model]["associations"],
                "internalId": output_models[model]["primary_key"]["Name"]
            }

            json_object = json.dumps(json_file, indent=4)
            Path(args.output_path).mkdir(parents=True, exist_ok=True)
            with open(os.path.join(args.output_path, f"{model}.json"), "w") as file:
                file.write(json_object)
    except OSError as file_error:
        log(f"Couldn't write to file test: {file_error}")
    except Exception as model_exception:
        print(model_exception)
        log(f"An error occurred: {model_exception}")
        sys.exit(1)


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
            print(f"An error occurred, please view the log file for details!")
    except OSError as log_error:
        # Prints the occurred error
        print(f"An error occurred while writing the log file: {log_error}")


##############################


main()
