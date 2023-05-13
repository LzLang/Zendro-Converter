import json
import numpy as np
from datetime import datetime, date

ALLOWED_TYPES = ["string", "integer", "boolean"]
ZENDRO_TYPES = {
	'string'  : 'String',
	'integer' : 'Int',
	'boolean' : 'Boolean'
}

def logMSG(msg):
    try:
        with open("Log.txt", "a") as file:
            currentTime = datetime.now().strftime("%H:%M:%S")
            file.write(str(date.today())+" - "+currentTime+":\t"+msg+"\n")
    except:
        print("Not allowed to create or edit the log")

def readJSON(path, fname):
    try:
        with open(path+fname, "r") as file:
            data = json.load(file)
            return data
    except:
        logMSG("Couldn't open file: "+path+fname)
            
def writeJSON(path, fname, propData):
	try:
		json_object = json.dumps(propData, indent=4)
		with open(path+fname, "w") as file:
			file.write(json_object)
	except:
		logMSG("Couldn't open file: "+path+fname)
     
def getPropType(types):
	boolean_mask = np.nonzero(np.isin(ALLOWED_TYPES, types))[0]
	if len(boolean_mask):
		return ALLOWED_TYPES[boolean_mask[0]]
	return None
	
def getZendroTypes(types):
	propType = getPropType(types)
	if propType != None:
		return ZENDRO_TYPES[propType]
	return None
	
def getPropData(data):
	properties = data['properties']
	propData = {}
	for prop in properties:
		type = getZendroTypes(properties[prop]['type'])
		if type==None: continue
		propData[prop] = {
			'description' : properties[prop]['description'],
			'type' : type
		}
	return propData
