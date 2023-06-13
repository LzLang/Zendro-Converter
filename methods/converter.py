#   Imports
import sys
import convertAPI
##############################


#   Main code
# If not 3 arguments are given throw an error
if len(sys.argv) != 3:
    raise Exception("Use: python convert.py [input path] [output path]")
else:
    input_files = convertAPI.setup_hierarchy(sys.argv[1], sys.argv[2])
    for file in input_files:
        # Load the content of the json file
        json_file = convertAPI.read_json(file)
        # Filename of the output file
        output_filename = file[file.rfind("\\"):]
        # Generate data for the output file
        output_file = convertAPI.get_data(json_file)
        # Set Path for the output file
        output_path = file.replace(sys.argv[1], sys.argv[2])
        # Write the output file
        convertAPI.write_json(output_path, output_file)
