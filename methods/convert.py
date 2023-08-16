#   Imports
import sys
import convertAPI
import argparse
import os

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
                    choices=['sql', 'generic', 'zendro-server', 'cassandra', 'mongodb', 'neo4j', 'presto/trino', 'amazon-s3', 'distributed-data-model', 'adapter'],
                    default='sql')

# Define a primary key
parser.add_argument('-p', '--primary-key-name',
                    help='Name of the primary key.')

# Define the type of the primary key
parser.add_argument('-t', '--primary-key-type',
                    help='Type of the primary key.',
                    choices=['Int', 'String'],
                    default='Int')

##############################

#   Main code
# If not 3 arguments are given throw an error
# Parse arguments
args = parser.parse_args()
input_files = convertAPI.setup_hierarchy(args.input_path, args.output_path)
for file in input_files:
    # Load the content of the json file
    json_file = convertAPI.read_json(file)

    # Generate data for the output file
    if args.primary_key_name:
        output_file = {args.primary_key_name: args.primary_key_type}
    else:
        output_file = {os.path.splitext(os.path.basename(file))[0]+"_id": args.primary_key_type}

    for key in list(json_file):
        item = convertAPI.get_type(json_file[key])
        if item is not None:
            output_file[key] = item
    # Set Path for the output file
    output_path = file.replace(args.input_path, args.output_path)
    # Write the output file
    convertAPI.write_json(output_path, output_file, args)
