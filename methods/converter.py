import json

# open a json file as input
f = open('Study.json')
# open a test file for output
file = open('test-0.0.1.txt', 'a')

# read/load the data from the json file
data = json.load(f)

# iterate through the data a write it to the output-file
for i in data:
    file.write(i+"\n")
    for j in data[i]:
        file.write(j+"\n")
    file.write("\n")
        
# close the files
file.close()
f.close()
