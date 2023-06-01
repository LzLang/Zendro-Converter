# Zendro-Converter
A script to convert data from BrAPI to Zendro-API
ToDo:
	- Testing with different/other files
	- Checking if output is correct or if properties are missing
	- Writing a function, that goes through the file system/directories and read the JSON-files automtically
	- Documentation still needed
	- Further testing


01.06.2023: 
	convert v0.0.6
	Goal: Get input from startup arguments
	Example: python convert.py "..\BrAPI_JSON_Schema_2-1\schemas\BrAPI-Core\Study.json" "..\results"
	--> First argument: convert.py
	--> Second argument: Path to input file 
	--> Third argument: Path to output folder (outputfile is named after input file)
	Observation: Currently only one file at a time, planing to give just the path and automatically searches and opens json files
	-----------------
	convertAPI v0.0.2
	Goal: Cleaning up the file
	--> Commented every function 
	--> Changed names of functions and variables to a more readable and suitable name
	--> Changed Exception handling (when opening a file excepts specifically OSError logs the occured error)
	--> Merged getPropType and getZendroType to get_type for a better overview


13.05.2023: Creating a git-repository
  Goal: Better version control, traceability and accessibility
  Uploaded every version until now (current version: v0.0.5)


12.05.2023:	Script v0.0.5 - Cleaning up the script
	Goal: Writing a class just fot the functions (modularization)
	--> logMSG(msg):						Write a msg with date and time to a log
	--> readJSON(path, fname):				Read in a JSON-file
	--> writeJSON(path, fname, propData):	Write data from properties to a JSON-file
	--> getPropType(types):					Return compatible/allowed types
	--> getZendroType(types):				Convert and return the Zendro types
	--> getPropData(data):					Return a dictionary with only properties, that have a Zendro compatible type
	Observation: Only properties with compatible types are exported to the JSON-file


11.05.2023: Script v0.0.4 - Extract only allowed data types
	Goal: Extract only properties with data types that are compatible with Zendro
	--> Using numpy to check if data types are compatible 
	Observation: Some properties are extracted without their data type


11.05.2023:	Script v0.0.3 - Extracting further informations
	Goal: Extract and write a file with the description and types of every property
	Observation: types are saved as array, further extraction needed


11.05.2023:	Script v0.0.2 - Extracting only the "properties"
	Goal: Extracting only the necessary informations (in this case the properties)
	--> Creating a test-file to test if extraction is working
	Observation: Extraction is working, input is stored as dictionary


11.05.2023:	Script v0.0.1 - First try to use a JSON-file as input
	Goal: Understanding the json module and how it's reading files
	--> Creating a test-file to write the input
	Observation: json module is usefule and will be used for this project
