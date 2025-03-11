import os
import re
import sys
import json
import argparse
import traceback
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

excluded_models = []


##############################


# Create parser for command-line options
parser = argparse.ArgumentParser(
    prog='Converter',
    description='Converts BrAPI json-schemas to a Zendro data model'
)

# Input path of the models
parser.add_argument('-i', '--input-path',
                    help='Path to the BrAPI schemas.',
                    required=True)

# Output path of the models
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
    output_models = get_properties(input_models)

    # Write conversed models
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
        # Read in every model
        files_data = {}
        for file in input_files:
            with open(file, "r") as open_file:
                models = json.load(open_file)['$defs']
                for current_model in models:
                    # Check if model is an enum -> Enums are incompatible to Zendro
                    if "enum" in models[current_model]:
                        log(f"{current_model}\t-\tIs an enum and is not supported!")
                        excluded_models.append(current_model)
                        continue
                    # Check if the model has any properties
                    if "properties" not in models[current_model] and not any(keyword in models[current_model] for keyword in ["oneOf", "allOf", "additionalProperties"]):
                        log(f"{current_model}\t-\tDoesn't have properties!")
                        continue

                    # Separate model in dictionaries for more overview
                    files_data[current_model] = {}
                    files_data[current_model]["attributes"] = {}
                    files_data[current_model]["associations"] = {}
                    files_data[current_model]["primary_key"] = {}

                    # Check if there is an "allOf" or "OneOf" in the model
                    # allOf -> include all properties of the referenced model
                    if not "properties" in models[current_model] and "allOf" in models[current_model]:
                        if "$ref" in models[current_model]["allOf"][0]:
                            files_data[current_model]["properties"] = models[current_model]["allOf"][1]["properties"]
                            files_data[current_model]["allOf"] = models[current_model]["allOf"][0]["$ref"].split("/")[-1]
                        else:
                            files_data[current_model]["properties"] = models[current_model]["allOf"][0]["properties"]
                            files_data[current_model]["allOf"] = models[current_model]["allOf"][1]["$ref"].split("/")[-1]
                    # oneOf -> user can decide which property should be used
                    elif not "properties" in models[current_model] and "oneOf" in models[current_model]:
                        prompt = "Model with oneOf property detected.\nPlease choose between one property (enter number):"
                        for index, oneOf_property in enumerate(models[current_model]["oneOf"]):
                            prompt += f"\n{index}: {oneOf_property["title"]}"
                        prompt += "\nChosen property:\t"
                        # Repeat user input, until there is a correct input
                        while True:
                            user_input = input(prompt)

                            if user_input.isdigit() and int(user_input) in range(0,len(models[current_model]["oneOf"])):
                                files_data[current_model]["properties"] = models[current_model]["oneOf"][int(user_input)]["properties"]
                                break
                            else:
                                print("Wrong input, please enter only the number you see!")

                    # If the model has a properties tag, then copy properties into our dictionary
                    elif "properties" in models[current_model]:
                        files_data[current_model]['properties'] = models[current_model]['properties']
                    # If the model has an "additionalProperties" tag, then add two necessary infos
                    elif "additionalProperties" in models[current_model]:
                        files_data[current_model]['properties'] = {
                            "additionalInfoDbId": {
                                "description": "the unique identifier for an additional info",
                                "type": "string"
                            },
                            "additionalProperties": {
                                "description": "A free space containing any additional information related to a particular object. A data source may provide any JSON object, unrestricted by the BrAPI specification.",
                                "type": "string"
                            }
                        }
                    else:
                        log(f"{current_model}: No properties!")
                        del files_data[current_model]


        return files_data if files_data else None

    except OSError as file_error:
        log(f'Couldn\'t open files: {file_error}')
    except Exception as model_exception:
        print(model_exception)
        log(f'An error occurred: {model_exception}')
        sys.exit(1)

def get_properties(models):
    """
    Get of all models, extract and convert the models to Zendro and return it.

    :param models: Dictionary of models
    :return: Formatted and converted dictionary of models
    """
    # For loop over all models
    for current_model in models:
        # Check if there is a custom primary key defined
        if f'{current_model[0].lower() + current_model[1:]}DbId' not in models[current_model]["properties"]:
            # Re expression to search for DbId
            if any(re.search("DbId$", re_property) for re_property in models[current_model]["properties"]):
                primary_key = next((key for key in models[current_model]["properties"] if re.search(r"DbId\b", key)), None)
            # Re expression to search for id and change it to DbId
            elif any(re.search("Id$", re_property) for re_property in models[current_model]["properties"]):
                pattern = r"Id\b"
                models[current_model]["properties"] = {
                    re.sub(pattern, "DbId", key): value
                    for key, value in models[current_model]["properties"].items()
                }
                primary_key = next((key for key in models[current_model]["properties"] if re.search(r"DbId\b", key)), None)
            else:
                models[current_model]["properties"][
                    f"{current_model[0].lower() + current_model[1:]}DbId"] = "String"
                primary_key = f"{current_model[0].lower() + current_model[1:]}DbId"
        else:
            primary_key = f"{current_model[0].lower() + current_model[1:]}DbId"

        if args.primary_key_name:
            models[current_model]["properties"][args.primary_key_name] \
                = models[current_model]["properties"].pop(primary_key)
            primary_key = args.primary_key_name

        if args.primary_key_type:
            primary_key_type = args.primary_key_type
        else:
            primary_key_type = models[current_model]["properties"][primary_key]["Type"]

        # Save primary key information about the model
        models[current_model]["primary_key"] = {
            "Name": primary_key,
            "Type": primary_key_type
        }

        # allOf -> include properties of referenced model
        if "allOf" in models[current_model]:
            target = models[current_model]["allOf"]
            models[current_model]["properties"].update(models[target]["properties"])
            del models[current_model]["allOf"]

        foreign_keys = {}
        for model_property in models[current_model]["properties"]:
            current_property = models[current_model]["properties"][model_property]

            # Check if property is an association
            if "items" in current_property and "$ref" in current_property["items"] or "$ref" in current_property:

                if "relationshipType" not in current_property:
                    if model_property.lower() not in [model_excluded.lower() for model_excluded in excluded_models]:
                        log(f"{current_model}:\t{model_property} - No relationshipType!")
                    continue

                association_relationship_type = current_property["relationshipType"].replace("-", "_")

                if "items" in current_property:
                    association_target = current_property["items"]["$ref"].split("/")[-1]
                else:
                    association_target = current_property["$ref"].split("/")[-1]
                if "referencedAttribute" not in current_property:
                    referenced_attribute = current_model[0].lower() + current_model[1:]
                else:
                    referenced_attribute = current_property["referencedAttribute"]

                # Check relationship type
                match association_relationship_type:
                    case "many_to_one":
                        target_key = f'{referenced_attribute}_IDs'
                        source_key = f'{model_property}_ID'
                        foreign_keys[source_key] = "String"
                    case "one_to_many":
                        target_key = f'{referenced_attribute}_ID'
                        source_key = f'{model_property}_IDs'
                        foreign_keys[source_key] = "[ String ]"
                    case "many_to_many":
                        target_key = f'{referenced_attribute}_IDs'
                        source_key = f'{model_property}_IDs'
                        foreign_keys[source_key] = "[ String ]"
                    case "one_to_one":
                        target_key = f'{referenced_attribute}_ID'
                        source_key = f'{model_property}_ID'
                        foreign_keys[source_key] = "String"
                    case _:
                        log(f'Model: {current_model}\tProperty: {model_property}\t !Wrong association type!')
                        continue

                # Check if the association target exists
                if association_target not in models:
                    if model_property != "additionalInfo" and association_target not in excluded_models:
                        log(f"{current_model} \t {model_property}\t {association_target}: Model not found")
                    continue
                elif "properties" not in models[association_target] and referenced_attribute not in \
                        models[association_target]["attributes"] or \
                        "properties" in models[association_target] and referenced_attribute not in \
                        models[association_target]["properties"]:
                    reverse_association = get_reverse_association(association_relationship_type)

                    # Save reverse association information in the target model
                    models[association_target]["associations"][referenced_attribute] = {
                        "type": reverse_association["association"],
                        "implementation": "foreignkeys",
                        "reverseAssociation": model_property,
                        "target": current_model.lower(),
                        "targetKey": source_key,
                        "sourceKey": target_key,
                        "keysIn": association_target.lower(),
                        "targetStorageType": args.storage_type
                    }
                    models[association_target]["attributes"].update({target_key: reverse_association["type"]})

                # Save association information in the current model
                models[current_model]["associations"][model_property] = {
                    "type": association_relationship_type,
                    "implementation": "foreignkeys",
                    "reverseAssociation": referenced_attribute,
                    "target": association_target.lower(),
                    "targetKey": target_key,
                    "sourceKey": source_key,
                    "keysIn": current_model.lower(),
                    "targetStorageType": args.storage_type
                }
            # Property is not an association
            else:
                # Check if a custom primary key type is set
                if args.primary_key_type:
                    property_type = args.primary_key_type
                else:
                    property_type = get_property_type(current_property)

                models[current_model]["primary_key"].update({"Type": f"{args.primary_key_type}"})

                # Check if the property has a compatible type and get property information
                # Else continue/skip the property
                if property_type:
                    description = ""
                    if "description" in current_property:
                        description = current_property['description'].replace("'", "\'")
                        description.replace('"', "\"")
                    models[current_model]["attributes"][model_property] = {
                        "type": property_type,
                        "description": description
                    }
                else:
                    continue

        # Add/update the attribute with the foreign keys
        models[current_model]["attributes"].update(foreign_keys)

    # After finishing a model it gets deleted
    for current_model in models:
        del models[current_model]["properties"]
    return models

def get_reverse_association(association):
    """
    Get the reverse association and set the type. \n
    Return reverse association, per default it's one_to_one.

    :param association: The current association frm witch we want the reverse association.
    :return: reverse association and it's type.
    """

    reverse_association = {}
    # Get reverse association, per default it's a one_to_one association
    match association:
        case "many_to_one":
            reverse_association["association"] = "one_to_many"
            reverse_association["type"] = "[ String ]"
        case "one_to_many":
            reverse_association["association"] = "many_to_one"
            reverse_association["type"] = "String"
        case "many_to_many":
            reverse_association["association"] = "many_to_many"
            reverse_association["type"] = "[ String ]"
        case _:
            reverse_association["association"] = "one_to_one"
            reverse_association["type"] = "String"
    return reverse_association

def get_property_type(input_property):
    """
    Checks the passed item for a Zendro compatible type and return it.

    :param input_property: An item from a json file (a dictionary).
    :return: Returns Zendro compatible type or none.
    """

    property_type = None
    if 'type' in input_property:
        # if the properties has no compatible type it is not needed therefore None is returned
        if isinstance(input_property['type'], list):
            for item_type in input_property['type']:
                if item_type == "array":
                    if input_property["items"]["type"] == "array":
                        property_type = f'[ {ZENDRO_TYPES[input_property["items"]["items"]["type"]]} ]'
                    else:
                        property_type = f'[ {ZENDRO_TYPES[input_property["items"]["type"]]} ]'
                if item_type in BrAPI_TYPES:
                    property_type = ZENDRO_TYPES[item_type]
        else:
            if input_property['type'] in BrAPI_TYPES:
                property_type = ZENDRO_TYPES[input_property['type']]

    return property_type

def write_json(output_models):
    """
    Writes the converted models to their own json file.

    :param output_models: Dictionary with model definitions compatible to Zendro
    :return: None: Nothing is returned
    """
    try:
        for model in output_models:
            # Create a json file with all model information in Zendro standard
            json_file = {
                "model": model.lower(),
                "storageType": args.storage_type,
                "attributes": output_models[model]["attributes"],
                "associations": output_models[model]["associations"],
                "internalId": output_models[model]["primary_key"]["Name"]
            }

            # Set correct indent and write it to file
            json_object = json.dumps(json_file, indent=4)
            Path(args.output_path).mkdir(parents=True, exist_ok=True)
            with open(os.path.join(args.output_path, f'{model.lower()}.json'), "w") as file:
                file.write(json_object)
    except OSError as file_error:
        log(f'Couldn\'t write to file test: {file_error}')
    except Exception as model_exception:
        print("Exception occured!")
        traceback.print_exc()
        log(f"An error occurred: {repr(model_exception)}")
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
            file.write(f'{str(date.today())} - {current_time}:\t{msg}\n')
            print(msg)
            #print(f'An error occurred, please view the log file for details!')
    except OSError as log_error:
        # Prints the occurred error
        print(f'An error occurred while writing the log file: {log_error}')


##############################


main()