#   Imports
import sys
import convertAPI
##############################


#   Main code
# If not 3 arguments are given throw an error
if len(sys.argv) != 3:
    raise Exception("Use: python convert.py [input file] [output folder]")
else:
    # Load the content of the json file
    input_file = convertAPI.read_json(sys.argv[1])
    # Path, were the output file should be stored / placed
    output_path = sys.argv[2]
    # Get name of the input file and set it as filename for the output
    output_filename = sys.argv[1][sys.argv[1].rfind("\\"):]

    # Get properties with Zendro compatible datatype from the input file
    properties = convertAPI.get_data(input_file)
    # Write the properties to a json output file
    convertAPI.write_json(output_path, output_filename, properties)
