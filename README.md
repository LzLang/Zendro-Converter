# Zendro-Converter
A script to convert data from BrAPI to Zendro-API
## ToDo:
- [x] Testing with different/other files
- [ ] Checking if output is correct or if properties are missing
- [x] Writing a function, that goes through the file system/directories and read the JSON-files automtically
- [x] Writing a function, that creates a corresponding file system/directories ibn the output folder
- [ ] Documentation still needed
- [ ] Further testing
- [ ] Rework `get_data` to consider properties, that have no `description`
	- [x] Properties with no `description` are considered
	- [ ] Nested properties are not skipped, if outer propertie has no compatible type
- [ ] Rework the Readme.md
	- [ ] Creating a example of how the code works

---

## 15.07.2023
### Goal: Understanding of command line arguments
Trying to understand [Issue 5 (Include model name and storage type in Zendro model definitions)](/../../issues/5) and implement it.

Observation: Working with command line arguments is quite easy, but still need to understand how to use e.g. "Help" or give a hint to the user.

Example of [Study](results/BrAPI-Core/Study.json):
```json
{
    "model": "Study",
    "storageType": "sql",
    "attributes": {
        "primary_id": "Int",
        "active": {
            "description": "Is this study currently active",
            "type": "Boolean"
        },
        "commonCropName": {
            "description": "Common name for the crop associated with this study",
            "type": "String"
        },
        "culturalPractices": {
            "description": "MIAPPE V1.1 (DM-28) Cultural practices - General description of the cultural practices of the study.",
            "type": "String"
        }
}
```

---

## 21.06.2023
### Goal: Writing a Unit-Test

Created the Unit-Test [Test_Food](BrAPI_JSON_Schema_2-1/Test_Food.json) with an [expected output](results/Test_Food_expected.json) and a [generated output](old_results/Test_Food_old.json).

Observation: The generated output is not the same as the expected one. The property `HotDog` still have the item `toppings` even though it's empty.

Solution: If returned dictionary is empty, than don't include it. Therefore modified `get_data`:

From:
```python
elif type(value) is dict:
	data[key] = get_data(value)
```

To:
```python
elif type(value) is dict:
	returned_data = get_data(value)
	if returned_data:
		data[key] = returned_data
```

Observation: [Generated output](results/Test_Food.json) is now identicall to the [expected output](results/Test_Food_expected.json).

Therefor the problem is solved.

---
## 19.06.2023
### Goal: Reworking `get_data(file_data)` to solve the no description problem

`get_data` now walks recursive through a dictionary and returns the compatible properties.
```python
def get_data(file_data):
    """
    From the passed data the properties are extracted.
    :param file_data: Data from a json file (a dictionary)
    :return: Properties with a compatible type to Zendro
    """

    data = {}
    # walk through the items of the dictionary
    for key, value in file_data.items():
        if key.lower() == 'description':
            data[key] = value
        elif key.lower() == 'type':
            zendro_type = get_type(value)
            # if the properties has no compatible type it is not needed therefore None is returned
            # otherwise the zendro type is assigned
            if zendro_type is None:
                return None
            data[key] = zendro_type
        # if the current item is itself a dictionary than call itself with the dictionary
        elif type(value) is dict:
            data[key] = get_data(value)
    return data
```

Observation: Even properties that has no description are returned.
Newe problem: If it is a nested propertie and the outer part has no compatible type, the whole propertie is skipped.
Example:
```json
"additionalInfo": {
            "additionalProperties": {
                "type": "string"
            },
            "description": "Additional arbitrary info",
            "type": [
                "null",
                "object"
            ]
        },
```

`additionalInfo` is currently skipped because itself has no compatible type, but the nested propertie `additionalProperties` has a compatible type.

Solution: Only skip the outer type and still use the inner type or use as type `none` if no compatible type is found.

I have to talk with my superior about this problem and the desired solution.

---

## 13.06.2023
### Goal: Working on a workaround for `get_data` to consider properties, that have no `description`

Reality: Reworked the `Readme.md` for a better readability
- Splitted the `Readme.md` into different sections
- Reworked the ToDo-List

---

## 12.06.2023
### 1. Goal: Automatic walkign through an input path and generating a corresponding hierarchy in the output path

Call: `python convert.py "..\BrAPI_JSON_Schema_2-1\schemas" "..\results"`
- Implemented `setup_hierarchy(input_path, output_path)` into convertAPI
	- `input_path`<br />Path to the input hierarchy, that sould be walked through
	- `output_path`<br />Path to the output hierarchy, where the input hiearchy should be created and where the files should be stored
	- Walks through the input path and saves all found json file toe analyse them, also saved the hierarchy to create a corresponding in the output path.
	- Calls `create_output_hierarchy` to create the corresponding hierarchy in the output path
	- Returns a list of the found files
 - Implemented `create_output_hierarchy(output_path, hierarchy)`
	 - `output_path`<br /> Path where the hierarchy should be created
	 - `hierarchy`<br />List of relativ paths to create the output hierarchy
	 - Logs an error, if hierarchy in the folder already exists
  - Reworked `write_json`
	  - `write_json(path, filename, properties)`  →  `write_json(path, properties)`
  	  - By searching the input directory for JSON files, the files now contain the absolute path, so a separate file name is no longer needed
   
Observation: Receiving an error `'description': properties[current_property]['description']`  →  `KeyError: 'description'`

Solution: Noticed that some json files have a different structur.

`documentationURL` from `List.json`
```json
"documentationURL": {
	"description": "A URL to the human readable documentation of this object",
        "format": "uri",
        "type": [
        	"null",
                "string"
        ]
}
```

`externalReferences` from `List.json`
```json
"externalReferences": {
	"description": "An array of external reference ids. These are references to this piece of data in an external system. Could be a simple string or a URI.",
        "items": {
        	"properties": {
                	"referenceId": {
                        	"description": "The external reference ID. Could be a simple string or a URI.",
                        	"type": [
                            		"null",
                            		"string"
                        	]
                    	},
                    	"referenceSource": {
                        	"description": "An identifier for the source system or database of this reference",
                        	"type": [
	                            	"null",
					"string"
                        	]
                    	}
                },
                "required": [
                	"referenceId",
                    	"referenceSource"
                ],
                "type": "object"
        },
        "title": "ExternalReferences",
        "type": [
        	"null",
                "array"
	]
}
```
Implemented, that `get_data` skip a properties if it has no `description`.

Goal for the future: Also consider these properties and implement a functional workaround.

### 2. Goal: Cleaning up the code
- Reworked the comments on each function
- Restructured the convertAPI code  →  Alter the position of the functions in the code for a better overview
---

## 01.06.2023 

### 1. Goal: Cleaning up the file
- Commented every function
- Changed names of functions and variables to a more readable and suitable name
- Changed Exception handling (when opening a file excepts specifically OSError logs the occured error)
- Merged getPropType and getZendroType to get_type for a better overview



### 2. Goal: Get input from startup arguments
Example: `python convert.py "..\BrAPI_JSON_Schema_2-1\schemas\BrAPI-Core\Study.json" "..\results"`
- **First argument**: convert.py
- **Second argument**: Path to input file 
- **Third argument**: Path to output folder (outputfile is named after input file)\n

Observation: Currently only one file at a time, planing to give just the path and automatically searches and opens json files

---

## 13.05.2023
### Goals:
- Creating a git-repository
- Better version control, traceability and accessibility
- Uploaded every version until now (current version: v0.0.5)

---

## 12.05.2023
### Goal: Writing a class just fot the functions (modularization)
- `logMSG(msg)`<br />Write a msg with date and time to a log
- `readJSON(path, fname)`<br />Read in a JSON-file
- `writeJSON(path, fname, propData)`<br />Write data from properties to a JSON-file
- `getPropType(types)`<br />Return compatible/allowed types
- `getZendroType(types)`<br />Convert and return the Zendro types
- `getPropData(data)`<br />Return a dictionary with only properties, that have a Zendro compatible type

Observation: Only properties with compatible types are exported to the JSON-file

---

## 11.05.2023:
### 1. Goal: Understanding the json module and how it's reading files
- Creating a test-file to write the input

Observation: json module is usefule and will be used for this project



### 2. Goal: Extracting only the necessary informations (in this case the properties)
- Creating a test-file to test if extraction is working

Observation: Extraction is working, input is stored as dictionary



### 3. Goal: Extract only properties with data types that are compatible with Zendro
- Using numpy to check if data types are compatible

Observation: Some properties are extracted without their data type



### 4. Goal: Extract and write a file with the description and types of every property

Observation: types are saved as array, further extraction needed
