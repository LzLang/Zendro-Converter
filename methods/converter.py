import convertAPI as API

input = API.readJSON("", "Study.json")

propData = API.getPropData(input)
API.writeJSON("", "test-0.0.5.json", propData)
