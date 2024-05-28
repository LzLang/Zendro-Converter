import os
import sys
import json
from datetime import datetime, date

BrAPI_TYPES = ["string", "integer", "boolean", "number"]
ZENDRO_TYPES = {
    'string': 'String',
    'integer': 'Int',
    'boolean': 'Boolean',
    'number': 'Float'
}


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
    model_properties = {
        "attributes": {},
        "associations": {}
    }
    foreign_keys = {}

    for model_property in input_model_properties:
        current_property = input_model_properties[model_property]
        if "relationshipType" not in current_property:
            property_type = get_property_type(current_property, current_model, model_property)
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
                    target_key = f"{current_property["referencedAttribute"]}_ids"
                    source_key = f"{model_property}_id"
                    foreign_keys[source_key] = "String"
                case "one_to_many":
                    target_key = f"{current_property["referencedAttribute"]}_id"
                    source_key = f"{model_property}_ids"
                    foreign_keys[source_key] = "[ String ]"
                case "many-to-many":
                    target_key = f"{current_property["referencedAttribute"]}_ids"
                    source_key = f"{model_property}_ids"
                    foreign_keys[source_key] = "[ String ]"
                case _:
                    target_key = f"{current_property["referencedAttribute"]}_id"
                    source_key = f"{model_property}_id"
                    foreign_keys[source_key] = "String"

            model_properties["associations"][model_property] = {
                "type": association_relationship_type,
                "implementation": "foreignkeys",
                "reverseAssociation": current_property["referencedAttribute"],
                "target": association_target,
                "targetKey": target_key,
                "sourceKey": source_key,
                "keysIn": current_model,
                "targetStorageType": "sql"
            }

        model_properties["attributes"].update(foreign_keys)
    return model_properties

def get_property_type(input_property, current_model, model_property):
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

def write_json(input_models):
    try:
        for model in input_models:
            json_file = {
                "model": model,
                "storageType": "sql",
                "attributes": input_models[model]["attributes"],
                "associations": input_models[model]["associations"],
                "internalId": f"{model[0].lower()+model[1:]}DbId"
            }

            json_object = json.dumps(json_file, indent=4)

            with open(os.path.join("./results", f"{model}.json"), "w") as file:
                file.write(json_object)
    except OSError as file_error:
        log(f"Couldn't write to file test: {file_error}")
    except Exception as model_exception:
        print(model_exception)
        log(f"An error occurred: {model_exception}")
        sys.exit(1)

input_models = get_models(get_files("./schema/"))
output_models = {}
for model in input_models:
    output_models[model] = get_properties(input_models[model]["properties"], model)

write_json(output_models)
