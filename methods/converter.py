import json
import numpy as np

# Open json file
f = open('Study.json')
# Open text document
file = open('test-0.0.4.txt', 'a')

# load Data from json
data = json.load(f)
# Only properties are needed
properties = data['properties']

# Allowed data types
allowedTypes = ["boolean", "string"]

# Every property
for prop in properties:
    # current property
    property = properties[prop]
    # Description
    description = property['description']
    # Type
    type = property['type']
    
    # Checking if property has allowed data types
    boolean_mask = np.nonzero(np.isin(allowedTypes, type))[0]    
    if len(boolean_mask):
        file.write(prop+"\n"+"description: "+description+"\n"+"type: "+str(type[1])+"\n\n")

# close the files  
file.close()
f.close()
