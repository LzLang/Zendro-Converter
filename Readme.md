# Zendro model converter

This project was developed by a student at the Technical University of Bingen.
The aim of the project is to develop a converter that reads BrAPI JSON model schemas and translates them into a Zendro-compliant model schema.

Chapters:
- [Installation](#installation)
- [Usage/Examples](#usageexamples)
  - [General Usage](#general-usage)
  - [Regular example](#regular-example)
  - [Custom primary key and type](#custom-primary-key-and-type)
  - [Associations](#associations)
- [API Reference](#api-reference)
  - [Packages used](#packages-used)
  - [get_files](#get_files)
  - [get_items](#get_items)
  - [get_type](#get_type)
  - [get_references](#get_references)
  - [read_json](#read_json)
  - [write_json](#write_json)
  - [log](#log)
- [Support](#support)

---

## Installation

Install the project with git

```bash
  [Follows]
```

---

 
## Usage/Examples

#### General Usage:
```bash
python convert.py -i [input-path] -o [output-path] [other command-line arguments]
```

---

#### Regular example:
```bash
python convert.py -i "../BrAPI-Schema" -o "../results"
```

JSON Schema input:

```json
{
    "$defs": {
        "Study": {
            "properties": {
                "active": {
                    "description": "A flag to indicate if a Study is currently active and ongoing",
                    "type": [
                        "null",
                        "boolean"
                    ]
                },
                "additionalInfo": {
                    "additionalProperties": {
                        "type": "string"
                    },
                    "description": "A free space containing any additional information related to a particular object. A data source may provide any JSON object, unrestricted by the BrAPI specification.",
                    "type": [
                        "null",
                        "object"
                    ]
                },
                "commonCropName": {
                    "description": "Common name for the crop associated with this study",
                    "type": [
                        "null",
                        "string"
                    ]
                },
                "contacts": {
                    "description": "List of contact entities associated with this study",
                    "items": {
                        "properties": {
                            "contactDbId": {
                                "description": "The ID which uniquely identifies this contact\n\nMIAPPE V1.1 (DM-33) Person ID - An identifier for the data submitter. If that submitter is an individual, ORCID identifiers are recommended.",
                                "type": "string"
                            },
                            "email": {
                                "description": "The contacts email address\n\nMIAPPE V1.1 (DM-32) Person email - The electronic mail address of the person.",
                                "type": [
                                    "null",
                                    "string"
                                ]
                            },
                            "instituteName": {
                                "description": "The name of the institution which this contact is part of\n\nMIAPPE V1.1 (DM-35) Person affiliation - The institution the person belongs to",
                                "type": [
                                    "null",
                                    "string"
                                ]
                            },
                            "name": {
                                "description": "The full name of this contact person\n\nMIAPPE V1.1 (DM-31) Person name - The name of the person (either full name or as used in scientific publications)",
                                "type": [
                                    "null",
                                    "string"
                                ]
                            },
                            "orcid": {
                                "description": "The Open Researcher and Contributor ID for this contact person (orcid.org)\n\nMIAPPE V1.1 (DM-33) Person ID - An identifier for the data submitter. If that submitter is an individual, ORCID identifiers are recommended.",
                                "type": [
                                    "null",
                                    "string"
                                ]
                            },
                            "type": {
                                "description": "The type of person this contact represents (ex: Coordinator, Scientist, PI, etc.)\n\nMIAPPE V1.1 (DM-34) Person role - Type of contribution of the person to the investigation",
                                "type": [
                                    "null",
                                    "string"
                                ]
                            }
                        },
                        "required": [
                            "contactDbId"
                        ],
                        "type": "object"
                    },
                    "type": [
                        "null",
                        "array"
                    ]
                }
            }
        }
    },
    "$id": "https://brapi.org/Specification/BrAPI-Schema/BrAPI-Core/Study.json",
    "$schema": "http://json-schema.org/draft/2020-12/schema"
}
```

Zendro compatible output:
```json
{
    "model": "Study",
    "storageType": "sql",
    "attributes": {
        "study_ID": "String",
        "active": {
            "type": "Boolean",
            "description": "A flag to indicate if a Study is currently active and ongoing"
        },
        "commonCropName": {
            "type": "String",
            "description": "Common name for the crop associated with this study"
        }
    }
}
```

---

#### Custom primary key and type:
```bash
python convert.py -i "../BrAPI-Schema" -o "../results" -p "github" -t "Int"
```

Zendro compatible output:
```json
{
    "model": "Study",
    "storageType": "sql",
    "attributes": {
        "study_github_ID": "Int",
        "active": {
            "type": "Boolean",
            "description": "A flag to indicate if a Study is currently active and ongoing"
        },
        "commonCropName": {
            "type": "String",
            "description": "Common name for the crop associated with this study"
        }
    }
}
```
As you can see, the primary key (here `study_github_ID`) contains the custom primary key name `github` and the data type is Integer.
Each generated data model contains the custom primary key name and is of the specified type.

---

#### Associations

All associations/relationships are defined after Zendro's [paired-end foreign keys](https://zendro-dev.github.io/setup_root/data_models#paired-end-foreign-keys).

---

## API Reference

#### Packages used
- `os`
- `re`
- `json`
- `sys`
- `datetime`, `date` from `datetime`

---

#### get_files
Get all json files:

```python
get_files(input_path)
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `input_path` | `string` | Path to the input files/directories |

Walks through the input path, searches for json files and extracts the relative path to the json file for the output path.

Function returns all found files in the input hierachy.

---

#### get_items
Get all items/properties:
```python
get_items(file_data)
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `file_data`      | `dictionary` | Content of multiple json files as dictionary |

Get a formatted dictionary of data models with Zendro compatible data types and references (Ready to be writen in json format).

Function returns a formatted dictionary of data models compatible to Zendro.

---

#### get_type
Check for Zendro compatible types:
```python
get_types(item)
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `item`      | `dictionary` | Property/Attribute of a model definition |

Function returns a Zendro compatible type or none

---

#### get_references
Get all associations of a given property:
```python
get_references(item)
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `item`      | `dictionary` | Property/Attribute of a model definition |

Function returns a dictionary of the attributes associations or none.

---

#### read_json
Read in a json file:
```python
read_json(files, storage_type, primary_key_name, primary_key_type)
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `files`      | `List` | List of json files to be read |
| `storage_type`      | `String` | A Zendro compatible storage type (used database) |
| `primary_key_name`      | `String` | Name of the primary key |
| `primary_key_type`      | `dictionary` | Type of the primary key (Int or String) 

Function returns a dictionary of data model definitions.

---

#### write_json
Write the data to a json file:
```python
write_json(file_data, output_path, storage_type)
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `file_data`      | `dictionary` | A dictionary filled with model definitions |
| `output_path`      | `String` | Path where the converted files should be saved |
| `storage_type`      | `String` | A Zendro compatible storage type (used database) |

This function doesn't return anything.

---

#### log
Log a message:
```python
log(msg)
```
| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `msg`      | `String` | Message to log |

Writes the message to a log-file. and logs the date and time automatically.

This function doesn't return anything but will give out a text to your console.

---

## Support

In the current version, the converter does not support:
- Arrays of any kind, especially also not objects (the only exception are the associations)
- In the models generated by Zendro it is possible to assign the status `required` to attributes.
This addition cannot be made before Zendro generates the data models, so it is not possible to give this status to individual attributes using the converter.
