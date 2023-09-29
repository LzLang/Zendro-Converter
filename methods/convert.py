#   Imports
import convertAPI
import argparse

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

parser.add_argument('-a', '--association-type',
                    help='Type of associations.',
                    choices=['Int', 'String'],
                    default='String')

##############################

#   Main code
# Parse arguments
args = parser.parse_args()

# Search for json files and write them to a variable
input_files = convertAPI.get_files(args.input_path)

# Extract from all json files the data
file_data = convertAPI.read_json(input_files, args.storage_type, args.primary_key_name, args.primary_key_type, args.association_type)

# Get all Zendro compatible attributes and references
items = convertAPI.get_items(file_data)

# Write the Zendro data model definitions
convertAPI.write_json(items, args.output_path, args.storage_type)
