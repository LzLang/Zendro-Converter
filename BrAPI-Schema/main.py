import os
import json

# Aktuelles Verzeichnis durchgehen
current_directory = os.getcwd()

input_files = []

# Durch alle Unterverzeichnisse gehen
for root, dirs, files in os.walk("C:\\Users\\Laszl\\OneDrive - TH Bingen\\Projektarbeit\\BrAPI-Schema"):
    for filename in files:
        if os.path.splitext(filename)[1].lower() == '.json':
            input_files.append(os.path.join(root, filename))

file_data = {}
for file in input_files:
    with open(file, "r") as json_file:
        model = os.path.splitext(os.path.basename(file))[0]
        file_data.update({model: json.load(json_file)['$defs'][model]['properties']})

types = []
for model in file_data:
    for property in file_data[model]:
        if 'type' in file_data[model][property]:
            if not isinstance(file_data[model][property]['type'], list):
                if file_data[model][property]['type'] not in types:
                    types.append(type)
                    if file_data[model][property]['type'] in ['integer', 'number']:
                        print(f"model:{model}\tproperty:{property}\ttype: {file_data[model][property]['type']}")
            else:
                for type in file_data[model][property]['type']:
                    if type not in types:
                        types.append(type)
                    if type in ['integer', 'number']:
                        print(f"model:{model}\tproperty:{property}\ttype: {type}")

print(types)