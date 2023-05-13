import json

# open a json file as input
f = open('Study.json')
# open a test file for output
file = open('test-0.0.3.txt', 'a')

# read/load the data from the json file
data = json.load(f)
# extracting the properties
properties = data['properties']

# iterate through the data a write it to the output-file
for prop in properties:
    property = properties[prop]
    description = property['description']
    type = property['type']
    file.write(prop+"\n"+"description: "+description+"\n"+"type: "+str(type)+"\n\n")
        
# close the files
file.close()
f.close()
