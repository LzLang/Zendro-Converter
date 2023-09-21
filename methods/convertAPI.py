#   Imports
import os
import json
from datetime import datetime, date


##############################


#   Constants / Types used in Zendro
BrAPI_TYPES = ["string", "integer", "boolean", "number"]
ZENDRO_TYPES = {
    'string': 'String',
    'integer': 'Int',
    'boolean': 'Boolean',
    'number': 'Float'
}


ZENDRO_STORAGE_TYPES = ['sql', 'generic', 'zendro-server', 'cassandra', 'mongodb', 'neo4j',
                        'presto/trino', 'amazon-s3', 'distributed-data-model', 'adapter']


##############################


#   Functions
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
                input_files.append(os.path.join(root, filename))

    return input_files


def get_items(file_data):
    """
    Get a formatted dictionary of data models with Zendro compatible data types and references.\n
    Ready to be writen in json format.

    :param file_data: Content of multiple json files as dictionary
    :return: Formatted dictionary of data models compatible to Zendro
    """
    # Formatted dictionary attributes and associations
    items = {}
    # Walk through all data models in file_data
    for model in file_data:
        # Create for every model a separate dictionary
        items[model] = {}
        # Every models needs a primary key, for the database
        items[model]['primary_key'] = file_data[model]['primary_key']
        items[model]['internalId'] = {"internalId": list(file_data[model]['primary_key'])[0]}
        items[model]['attributes'] = {}
        items[model]['associations'] = {}
        reference_association_ids = {}

        # Walk through every property of a data model
        for item_property in file_data[model]['properties']:
            # Current property
            item = file_data[model]['properties'][item_property]
            # Description
            description = ""
            if 'description' in item:
                description = item['description'].replace("'", "\'")
                description.replace('"', "\"")
            # Get type of the current property
            item_type = get_type(item)

            # Check if property has a Zendro compatible data type
            if item_type:
                # Add property to the dictionary
                if description:
                    items[model]['attributes'].update({
                        item_property: {
                            "type": item_type,
                            "description": description
                        }
                    })
                else:
                    items[model]['attributes'].update({item_property: item_type})

            # Property may be an association, check if it is an association
            reference = get_reference(item)
            if reference:
                # Transform association to a Zendro compatible association
                target = reference['target']
                if target not in file_data:
                    log(f"{target} from {model} don't exist")
                    continue
                associated_attribute = reference['reverseAssociation']
                if associated_attribute not in file_data[target]['properties']:
                    log(f"{associated_attribute} in {target} from {model} don't exist")
                    continue
                target_key = f"{associated_attribute}_id"
                source_key = f"{item_property}_id"
                source_key_type = list(file_data[target]['primary_key'].values())[0]
                match reference['type']:
                    case 'many_to_one':
                        target_key = f"{associated_attribute}_ids"
                    case 'one_to_many':
                        source_key = f"{item_property}_ids"
                        source_key_type = f"[ {source_key_type} ]"
                    case 'many_to_many':
                        target_key = f"{associated_attribute}_ids"
                        source_key = f"{item_property}_ids"
                        source_key_type = f"[ {source_key_type} ]"
                target_key = ''.join(['_' + c.lower() if c.isupper() else c for c in target_key]).lstrip('_')
                source_key = ''.join(['_' + c.lower() if c.isupper() else c for c in source_key]).lstrip('_')

                items[model]['associations'].update({
                    item_property: {
                        'type': reference['type'],
                        'implementation': 'foreignkey',
                        'reverseAssociation': associated_attribute,
                        'target': reference['target'],
                        'targetKey': target_key,
                        'sourceKey': source_key,
                        'keysIn': model,
                        'targetStorageType': file_data[reference['target']]['targetStorageType']
                    }
                })

                reference_association_ids.update({source_key: source_key_type})
        
        items[model]['attributes'].update(reference_association_ids)
    return items if items else None


def get_type(item):
    """
    Checks the passed item for a Zendro compatible type and returns it
    :param item: An item from a json file (a dictionary)
    :return: Returns Zendro compatible type or none
    """
    # walk through the items of the dictionary
    zendro_item_type = None
    if 'type' in item:
        # if the properties has no compatible type it is not needed therefore None is returned
        if isinstance(item['type'], list):
            for item_type in item['type']:
                if item_type in BrAPI_TYPES:
                    zendro_item_type = ZENDRO_TYPES[item_type]
        else:
            if item['type'] in BrAPI_TYPES:
                zendro_item_type = ZENDRO_TYPES[item['type']]

    return zendro_item_type


def get_reference(item):
    """
    Get all associations of a given property

    :param item: Property of a model definition
    :return: A dictionary of the items association
    """

    # Checks a given item if it's an association
    # When it's an association extract all necessary information and return it, otherwise return none
    reference = {}
    if 'relationshipType' in item:
        reference['type'] = item['relationshipType'].replace('-', '_')
        reference['reverseAssociation'] = item['referencedAttribute']
        if '$ref' in item:
            reference['target'] = item['$ref'].split('/')[-1]
        else:
            reference['target'] = item['items']['$ref'].split('/')[-1]
    return reference if reference else None


def read_json(files, storage_type, primary_key_name, primary_key_type):
    """
    Reads in a json file and returns its content.

    :param files: List of Json files to be read
    :param storage_type: A Zendro compatible storage type (used database)
    :param primary_key_name: Name of the primary key
    :param primary_key_type: Type of the primary key (Int or String)
    :return: Returns a dictionary of data model definitions
    """
    try:
        # Raise an exception if storage_type or primary_key_type is not compatible
        if storage_type not in ZENDRO_STORAGE_TYPES:
            raise Exception('\'storage_type\' is not compatible to Zendro')
        if primary_key_type not in ['Int', 'String']:
            raise Exception('\'primary_key_type\' must be of type \'Int\' or \'String\'')

        # Open file and load json content
        file_data = {}
        for file in files:
            with open(file, "r") as json_file:
                # Get current model and save all model definitions to a dictionary
                model = os.path.splitext(os.path.basename(file))[0]
                model_id = ''.join(['_' + c.lower() if c.isupper() else c for c in model]).lstrip('_')
                if primary_key_name is (f"{model_id}_id" or f"{model_id}_ids"):
                    raise Exception("Name of the primary key can't be [model]_id or [model]_ids")
                file_data[model] = {}
                file_data[model]['targetStorageType'] = storage_type
                if primary_key_name:
                    file_data[model]['primary_key'] = {primary_key_name: primary_key_type}
                else:
                    file_data[model]['primary_key'] = {f"{model_id}_primary_key": primary_key_type}
                file_data[model].update({'properties': json.load(json_file)['$defs'][model]['properties']})
        return file_data if file_data else None
    except OSError as file_error:
        log(f"Couldn't open files: {file_error}")


def write_json(file_data, output_path, storage_type):
    """
    Writes the passed data to a json file.

    :param file_data: A dictionary filled with model definitions
    :param output_path: Path where the converted files should be saved
    :param storage_type: A Zendro compatible storage type (used database)
    """

    try:
        # Raise an exception if storage_type is not compatible
        if storage_type not in ZENDRO_STORAGE_TYPES:
            raise Exception('\'storage_type\' is not compatible to Zendro')
        # Format every model to write it to a json file as Zendro compatible data model definition
        for model in file_data:
            json_file = {
                'model': model,
                'storageType': storage_type,
                'database': 'default-sql',
                'attributes': file_data[model]['primary_key']
            }
            json_file['attributes'].update(file_data[model]['attributes'])

            # If a model has an association it is needed to be included
            if 'associations' in file_data[model]:
                json_file['associations'] = file_data[model]['associations']
            json_file.update(file_data[model]['internalId'])
            # Correct json format needed
            json_object = json.dumps(json_file, indent=4)
            # Write file
            with open(os.path.join(output_path, f"{model}.json"), "w") as file:
                file.write(json_object)
    except OSError as file_error:
        log(f"Couldn't write to file {output_path}: {file_error}")


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
