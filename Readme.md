# Zendro model converter

This project was developed by a student at the Technical University of Bingen.<br />
The aim of the project is to develop a converter that reads BrAPI JSON model schemas and translates them into a Zendro-compliant model schema.

Chapters:
- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage/Examples](#usageexamples)
  - [Required Arguments](#required-arguments)
  - [Optional Arguments](#optional-arguments)
  - [General Usage](#general-usage)
  - [Regular example](#regular-example)
  - [Custom primary key and type](#custom-primary-key-and-type)
  - [Associations](#associations)
- [Program Workflow](#program-workflow)
  - [Main Execution (`main()`)](#main-execution-main)
  - [File Handling (`get_files(input_path)`)](#file-handling-get_filesinput_path)
  - [Model Extraction (`get_models(input_files)`)](#model-extraction-get_modelsinput_files)
  - [Property Conversion (`get_properties(models)`)](#property-conversion-get_propertiesmodels)
  - [Association Handling (`get_reverse_association(association)`)](#association-handling-get_reverse_associationassociation)
  - [Property Type Conversion (`get_property_type(input_property)`)](#property-type-conversion-get_property_typeinput_property)
  - [Output Generation (`write_json(output_models)`)](#output-generation-write_jsonoutput_models)
  - [Logging (`log(msg)`)](#logging-logmsg)
- [Error Handling](#error-handling)
- [Notes](#notes)
- [Possible Improvements](#possible-improvements)

---

## Overview

This Python program converts BrAPI JSON schemas into Zendro-compatible data models.<br />It processes JSON schema files, extracts relevant model properties, and generates output files containing the converted model definitions.<br />The program supports command-line execution with customizable parameters for input/output paths, storage types, and primary keys.

---

## Prerequisites

- Python `3.x`
- Required modules:
  - `os`
  - `re`
  - `sys`
  - `json`
  - `argparse`
  - `traceback`
  - `datetime`
  - `pathlib`

---

## Installation

Install the project with git

```bash
  git clone https://github.com/LzLang/Zendro-Converter.git
```
The Python script is located in the main folder (`converter.py`).

---

 
## Usage/Examples

The script is executed via the command line with required and optional arguments:

### Required Arguments

- `-i`, `--input-path`: Path to the directory containing BrAPI JSON schemas.
- `-o`, `--output-path`: Path to the directory where the converted Zendro models will be saved.

### Optional Arguments

- `-s`, `--storage-type`: Specifies the storage type for the model.<br />Default: `sql`. Options include:
  - `sql`, `generic`, `zendro-server`, `cassandra`, `mongodb`, `neo4j`, `presto/trino`, `amazon-s3`
, `distributed-data-model`, `adapter`
- `-p`, `--primary-key-name`: Custom name for the primary key.
- `-t`, `--primary-key-type`: Type of the primary key. <br />Default: `String`. Options: `Int`, `String`.
#### General Usage:
```bash
python converter.py -i "./BrAPI-Schema" -o "./results" -s mongodb -p myPrimaryKey -t Int
```

---

#### Regular example:
```bash
python convert.py -i "./BrAPI-Schema" -o "./results"
```
<details>
<summary>Input: Study.json</summary>

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
                    "description": "A free space containing any additional information related to a particular object. A data source may provide any JSON object, unrestricted by the BrAPI specification.",
                    "$ref": "../BrAPI-Common/AdditionalInfo.json#/$defs/AdditionalInfo",
					"relationshipType": "one-to-one"
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
                    "relationshipType": "many-to-many",
                    "items": {
                        "$ref": "Contact.json#/$defs/Contact"
                    },
                    "type": [
                        "null",
                        "array"
                    ]
                },
                "culturalPractices": {
                    "description": "MIAPPE V1.1 (DM-28) Cultural practices - General description of the cultural practices of the study.",
                    "type": [
                        "null",
                        "string"
                    ]
                },
                "dataLinks": {
                    "description": "List of links to extra data files associated with this study. Extra data could include notes, images, and reference data.",
                    "items": {
                        "$ref": "DataLink.json#/$defs/DataLink"
                    },
                    "type": [
                        "null",
                        "array"
                    ]
                },
                "documentationURL": {
                    "description": "A URL to the human readable documentation of an object",
                    "format": "uri",
                    "type": [
                        "null",
                        "string"
                    ]
                },
                "endDate": {
                    "description": "The date the study ends\n\nMIAPPE V1.1 (DM-15) End date of study - Date and, if relevant, time when the experiment ended",
                    "format": "date-time",
                    "type": [
                        "null",
                        "string"
                    ]
                },
                "environmentParameters": {
                    "description": "Environmental parameters that were kept constant throughout the study and did not change between observation units.\n\nMIAPPE V1.1 (DM-57) Environment - Environmental parameters that were kept constant throughout the study and did not change between observation units or assays. Environment characteristics that vary over time, i.e. environmental variables, should be recorded as Observed Variables (see below).",
                    "relationshipType": "one-to-many",
                    "referencedAttribute": "study",
                    "items": {
                        "$ref": "../BrAPI-Core/Study.json#/$defs/EnvironmentParameters",
                        "description": "EnvironmentParameters"
                    },
                    "title": "EnvironmentParameters",
                    "type": [
                        "null",
                        "array"
                    ]
                },
                "experimentalDesign": {
                    "description": "The experimental and statistical design full description plus a category PUI taken from crop research ontology or agronomy ontology",
                    "relationshipType": "one-to-one",
                    "referencedAttribute": "study",
                    "$ref": "../BrAPI-Core/Study.json#/$defs/ExperimentalDesign"
                },
                "externalReferences": {
                    "description": "An array of external reference ids. These are references to this piece of data in an external system. Could be a simple string or a URI.",
                    "relationshipType": "one-to-many",
                    "items": {
                        "$ref": "../BrAPI-Common/ExternalReference.json#/$defs/ExternalReference",
                        "description": "ExternalReferences"
                    },
                    "title": "ExternalReferences",
                    "type": [
                        "null",
                        "array"
                    ]
                },
                "growthFacility": {
                    "description": "Short description of the facility in which the study was carried out.",
                    "relationshipType": "many-to-one",
                    "referencedAttribute": "study",
					"$ref": "../BrAPI-Core/Study.json#/$defs/GrowthFacility"
                },
                "lastUpdate": {
                    "description": "The date and time when this study was last modified",
                    "relationshipType": "one-to-one",
                    "referencedAttribute": "study",
                    "$ref": "../BrAPI-Core/Study.json#/$defs/LastUpdate"
                },
                "license": {
                    "description": "The usage license associated with the study data",
                    "type": [
                        "null",
                        "string"
                    ]
                },
                "location": {
                    "$ref": "Location.json#/$defs/Location",
                    "description": "The unique identifier for a Location",
                    "referencedAttribute": "studies",
                    "relationshipType": "many-to-one"
                },
                "observationLevels": {
                    "description": "Observation levels indicate the granularity level at which the measurements are taken. `levelName` \ndefines the level, `levelOrder` defines where that level exists in the hierarchy of levels. \n`levelOrder`s lower numbers are at the top of the hierarchy (ie field > 0) and higher numbers are \nat the bottom of the hierarchy (ie plant > 6). \n\n**Standard Level Names: study, field, entry, rep, block, sub-block, plot, sub-plot, plant, pot, sample** \n\nFor more information on Observation Levels, please review the <a target=\"_blank\" href=\"https://wiki.brapi.org/index.php/Observation_Levels\">Observation Levels documentation</a>. ",
                    "relationshipType": "one-to-many",
                    "items": {
                        "$ref": "../BrAPI-Common/ObservationUnitHierarchyLevel.json#/$defs/ObservationUnitHierarchyLevel",
                        "description": "ObservationLevels"
                    },
                    "title": "ObservationLevels",
                    "type": [
                        "null",
                        "array"
                    ]
                },
                "observationUnitsDescription": {
                    "description": "MIAPPE V1.1 (DM-25) Observation unit description - General description of the observation units in the study.",
                    "type": [
                        "null",
                        "string"
                    ]
                },
                "observationVariables": {
                    "description": "The list of Observation Variables being used in this study. \n\nThis list is intended to be the wishlist of variables to collect in this study. It may or may not match the set of variables used in the collected observation records. ",
                    "items": {
                        "$ref": "../BrAPI-Phenotyping/ObservationVariable.json#/$defs/ObservationVariable"
                    },
                    "referencedAttribute": "studies",
                    "relationshipType": "many-to-many",
                    "type": "array"
                },
                "seasons": {
                    "description": "List of seasons over which this study was performed.",
                    "items": {
                        "type": "string"
                    },
                    "type": [
                        "null",
                        "array"
                    ]
                },
                "startDate": {
                    "description": "The date this study started\n\nMIAPPE V1.1 (DM-14) Start date of study - Date and, if relevant, time when the experiment started",
                    "format": "date-time",
                    "type": [
                        "null",
                        "string"
                    ]
                },
                "studyCode": {
                    "description": "A short human readable code for a study",
                    "type": [
                        "null",
                        "string"
                    ]
                },
                "studyDbId": {
                    "description": "The ID which uniquely identifies a study within the given database server\n\nMIAPPE V1.1 (DM-11) Study unique ID - Unique identifier comprising the name or identifier for the institution/database hosting the submission of the study data, and the identifier of the study in that institution.",
                    "type": "string"
                },
                "studyDescription": {
                    "description": "The description of this study\n\nMIAPPE V1.1 (DM-13) Study description - Human-readable text describing the study",
                    "type": [
                        "null",
                        "string"
                    ]
                },
                "studyName": {
                    "description": "The human readable name for a study\n\nMIAPPE V1.1 (DM-12) Study title - Human-readable text summarising the study",
                    "type": "string"
                },
                "studyPUI": {
                    "description": "A permanent unique identifier associated with this study data. For example, a URI or DOI",
                    "type": [
                        "null",
                        "string"
                    ]
                },
                "studyType": {
                    "description": "The type of study being performed. ex. \"Yield Trial\", etc",
                    "type": [
                        "null",
                        "string"
                    ]
                },
                "trial": {
                    "$ref": "Trial.json#/$defs/Trial",
                    "description": "The ID which uniquely identifies a trial",
                    "referencedAttribute": "studies",
                    "relationshipType": "many-to-one"
                },
                "callSets": {
                    "title": "CallSets",
                    "description": "",
                    "referencedAttribute": "study",
                    "relationshipType": "one-to-many",
                    "items": {
                        "$ref": "../BrAPI-Genotyping/CallSet.json#/$defs/CallSet",
                        "description": "CallSet"
                    },
                    "type": [
                        "null",
                        "array"
                    ]
                },
                "plates": {
                    "title": "plates",
                    "description": "plates",
                    "referencedAttribute": "study",
                    "relationshipType": "one-to-many",
                    "items": {
                        "$ref": "../BrAPI-Genotyping/Plate.json#/$defs/Plate",
                        "description": "Plate"
                    },
                    "type": [
                        "null",
                        "array"
                    ]
                },
                "samples": {
                    "title": "samples",
                    "description": "samples",
                    "referencedAttribute": "study",
                    "relationshipType": "one-to-many",
                    "items": {
                        "$ref": "../BrAPI-Genotyping/Sample.json#/$defs/Sample",
                        "description": "Sample"
                    },
                    "type": [
                        "null",
                        "array"
                    ]
                },
                "variantSets": {
                    "title": "variantSets",
                    "description": "variantSets",
                    "referencedAttribute": "study",
                    "relationshipType": "one-to-many",
                    "items": {
                        "$ref": "../BrAPI-Genotyping/VariantSet.json#/$defs/VariantSet",
                        "description": "VariantSet"
                    },
                    "type": [
                        "null",
                        "array"
                    ]
                },
                "events": {
                    "title": "events",
                    "description": "events",
                    "referencedAttribute": "study",
                    "relationshipType": "many-to-many",
                    "items": {
                        "$ref": "../BrAPI-Phenotyping/Event.json#/$defs/Event",
                        "description": "Event"
                    },
                    "type": [
                        "null",
                        "array"
                    ]
                },
                "observations": {
                    "title": "observations",
                    "description": "observations",
                    "referencedAttribute": "study",
                    "relationshipType": "one-to-many",
                    "items": {
                        "$ref": "../BrAPI-Phenotyping/Observation.json#/$defs/Observation",
                        "description": "Observation"
                    },
                    "type": [
                        "null",
                        "array"
                    ]
                },
                "observationUnits": {
                    "title": "observationUnits",
                    "description": "observationUnits",
                    "referencedAttribute": "study",
                    "relationshipType": "one-to-many",
                    "items": {
                        "$ref": "../BrAPI-Phenotyping/ObservationUnit.json#/$defs/ObservationUnit",
                        "description": "ObservationUnit"
                    },
                    "type": [
                        "null",
                        "array"
                    ]
                }
            },
            "required": [
                "studyName",
                "studyDbId"
            ],
            "title": "Study",
            "type": "object",
            "brapi-metadata": {
                "primaryModel": true
            }
        },
        "EnvironmentParameters": {
            "properties": {
                "description": {
                    "description": "Human-readable value of the environment parameter (defined above) constant within the experiment",
                    "type": "string"
                },
                "environmentParametersDbId": {
                    "description": "Human-readable value of the environment parameter (defined above) constant within the experiment",
                    "type": "string"
                },
                "parameterName": {
                    "description": "Name of the environment parameter constant within the experiment\n\nMIAPPE V1.1 (DM-58) Environment parameter - Name of the environment parameter constant within the experiment. ",
                    "type": "string"
                },
                "parameterPUI": {
                    "description": "URI pointing to an ontology class for the parameter",
                    "type": [
                        "null",
                        "string"
                    ]
                },
                "unit": {
                    "description": "Unit of the value for this parameter",
                    "type": [
                        "null",
                        "string"
                    ]
                },
                "unitPUI": {
                    "description": "URI pointing to an ontology class for the unit",
                    "type": [
                        "null",
                        "string"
                    ]
                },
                "value": {
                    "description": "Numerical or categorical value\n\nMIAPPE V1.1 (DM-59) Environment parameter value - Value of the environment parameter (defined above) constant within the experiment.",
                    "type": [
                        "null",
                        "string"
                    ]
                },
                "valuePUI": {
                    "description": "URI pointing to an ontology class for the parameter value",
                    "type": [
                        "null",
                        "string"
                    ]
                },
                "study": {
                    "description": "Environment parameters associated with a study",
                    "$ref": "../BrAPI-Core/Study.json#/$defs/Study",
                    "relationshipType": "many-to-one",
                    "referencedAttribute": "environmentParameters"
                }
            },
            "required": [
                "environmentParametersDbId",
                "parameterName",
                "description"
            ],
            "title": "EnvironmentParameters",
            "type": "object",
            "brapi-metadata": {
                "primaryModel": false
            }
        },
        "ExperimentalDesign": {
            "properties": {
                "PUI": {
                    "description": "MIAPPE V1.1 (DM-23) Type of experimental design - Type of experimental  design of the study, in the form of an accession number from the Crop Ontology.",
                    "type": [
                        "null",
                        "string"
                    ]
                },
                "description": {
                    "description": "MIAPPE V1.1 (DM-22) Description of the experimental design - Short description of the experimental design, possibly including statistical design. In specific cases, e.g. legacy datasets or data computed from several studies, the experimental design can be \"unknown\"/\"NA\", \"aggregated/reduced data\", or simply 'none'.",
                    "type": [
                        "null",
                        "string"
                    ]
                },
                "study": {
                    "description": "Experimental design associated with a study",
                    "$ref": "../BrAPI-Core/Study.json#/$defs/Study",
                    "relationshipType": "many-to-one",
                    "referencedAttribute": "experimentalDesign"
                }
            },
            "title": "ExperimentalDesign",
            "type": "object",
            "brapi-metadata": {
                "primaryModel": false
            }
        },
        "GrowthFacility": {
            "properties": {
                "PUI": {
                    "description": "MIAPPE V1.1 (DM-27) Type of growth facility - Type of growth facility in which the study was carried out, in the form of an accession number from the Crop Ontology.",
                    "type": [
                        "null",
                        "string"
                    ]
                },
                "description": {
                    "description": "MIAPPE V1.1 (DM-26) Description of growth facility - Short description of the facility in which the study was carried out.",
                    "type": [
                        "null",
                        "string"
                    ]
                },
                "study": {
                    "description": "Growth facility associated with a study",
                    "$ref": "../BrAPI-Core/Study.json#/$defs/Study",
                    "relationshipType": "many-to-one",
                    "referencedAttribute": "growthFacility"
                }
            },
            "title": "GrowthFacility",
            "type": "object",
            "brapi-metadata": {
                "primaryModel": false
            }
        },
        "LastUpdate": {
            "properties": {
                "lastUpdateDbId": {
                    "description": "The date and time when this study was last modified",
                    "type": "string"
                },
                "timestamp": {
                    "format": "date-time",
                    "type": [
                        "null",
                        "string"
                    ]
                },
                "version": {
                    "type": [
                        "null",
                        "string"
                    ]
                },
                "study": {
                    "description": "Last update associated with a study",
                    "$ref": "../BrAPI-Core/Study.json#/$defs/Study",
                    "relationshipType": "many-to-one",
                    "referencedAttribute": "lastUpdate"
                }
            },
            "required": [
                "lastUpdateDbId"
            ],
            "title": "LastUpdate",
            "type": "object",
            "brapi-metadata": {
                "primaryModel": false
            }
        }
    },
    "$id": "https://brapi.org/Specification/BrAPI-Schema/BrAPI-Core/Study.json",
    "$schema": "http://json-schema.org/draft/2020-12/schema"
}
```
</details>

<details>
<summary>Output: Study.json</summary>

```json
{
    "model": "study",
    "storageType": "sql",
    "attributes": {
        "active": {
            "type": "String",
            "description": "A flag to indicate if a Study is currently active and ongoing"
        },
        "commonCropName": {
            "type": "String",
            "description": "Common name for the crop associated with this study"
        },
        "culturalPractices": {
            "type": "String",
            "description": "MIAPPE V1.1 (DM-28) Cultural practices - General description of the cultural practices of the study."
        },
        "documentationURL": {
            "type": "String",
            "description": "A URL to the human readable documentation of an object"
        },
        "endDate": {
            "type": "String",
            "description": "The date the study ends\n\nMIAPPE V1.1 (DM-15) End date of study - Date and, if relevant, time when the experiment ended"
        },
        "license": {
            "type": "String",
            "description": "The usage license associated with the study data"
        },
        "observationUnitsDescription": {
            "type": "String",
            "description": "MIAPPE V1.1 (DM-25) Observation unit description - General description of the observation units in the study."
        },
        "seasons": {
            "type": "String",
            "description": "List of seasons over which this study was performed."
        },
        "startDate": {
            "type": "String",
            "description": "The date this study started\n\nMIAPPE V1.1 (DM-14) Start date of study - Date and, if relevant, time when the experiment started"
        },
        "studyCode": {
            "type": "String",
            "description": "A short human readable code for a study"
        },
        "studyDbId": {
            "type": "String",
            "description": "The ID which uniquely identifies a study within the given database server\n\nMIAPPE V1.1 (DM-11) Study unique ID - Unique identifier comprising the name or identifier for the institution/database hosting the submission of the study data, and the identifier of the study in that institution."
        },
        "studyDescription": {
            "type": "String",
            "description": "The description of this study\n\nMIAPPE V1.1 (DM-13) Study description - Human-readable text describing the study"
        },
        "studyName": {
            "type": "String",
            "description": "The human readable name for a study\n\nMIAPPE V1.1 (DM-12) Study title - Human-readable text summarising the study"
        },
        "studyPUI": {
            "type": "String",
            "description": "A permanent unique identifier associated with this study data. For example, a URI or DOI"
        },
        "studyType": {
            "type": "String",
            "description": "The type of study being performed. ex. \"Yield Trial\", etc"
        },
        "additionalInfo_ID": "String",
        "contacts_IDs": "[ String ]",
        "environmentParameters_IDs": "[ String ]",
        "experimentalDesign_ID": "String",
        "externalReferences_IDs": "[ String ]",
        "growthFacility_ID": "String",
        "lastUpdate_ID": "String",
        "location_ID": "String",
        "observationLevels_IDs": "[ String ]",
        "observationVariables_IDs": "[ String ]",
        "trial_ID": "String",
        "callSets_IDs": "[ String ]",
        "plates_IDs": "[ String ]",
        "samples_IDs": "[ String ]",
        "variantSets_IDs": "[ String ]",
        "events_IDs": "[ String ]",
        "observations_IDs": "[ String ]",
        "observationUnits_IDs": "[ String ]"
    },
    "associations": {
        "additionalInfo": {
            "type": "one_to_one",
            "implementation": "foreignkeys",
            "reverseAssociation": "study",
            "target": "additionalinfo",
            "targetKey": "study_ID",
            "sourceKey": "additionalInfo_ID",
            "keysIn": "study",
            "targetStorageType": "sql"
        },
        "contacts": {
            "type": "many_to_many",
            "implementation": "foreignkeys",
            "reverseAssociation": "study",
            "target": "contact",
            "targetKey": "study_IDs",
            "sourceKey": "contacts_IDs",
            "keysIn": "study",
            "targetStorageType": "sql"
        },
        "environmentParameters": {
            "type": "one_to_many",
            "implementation": "foreignkeys",
            "reverseAssociation": "study",
            "target": "environmentparameters",
            "targetKey": "study_ID",
            "sourceKey": "environmentParameters_IDs",
            "keysIn": "study",
            "targetStorageType": "sql"
        },
        "experimentalDesign": {
            "type": "one_to_one",
            "implementation": "foreignkeys",
            "reverseAssociation": "study",
            "target": "experimentaldesign",
            "targetKey": "study_ID",
            "sourceKey": "experimentalDesign_ID",
            "keysIn": "study",
            "targetStorageType": "sql"
        },
        "externalReferences": {
            "type": "one_to_many",
            "implementation": "foreignkeys",
            "reverseAssociation": "study",
            "target": "externalreference",
            "targetKey": "study_ID",
            "sourceKey": "externalReferences_IDs",
            "keysIn": "study",
            "targetStorageType": "sql"
        },
        "growthFacility": {
            "type": "many_to_one",
            "implementation": "foreignkeys",
            "reverseAssociation": "study",
            "target": "growthfacility",
            "targetKey": "study_IDs",
            "sourceKey": "growthFacility_ID",
            "keysIn": "study",
            "targetStorageType": "sql"
        },
        "lastUpdate": {
            "type": "one_to_one",
            "implementation": "foreignkeys",
            "reverseAssociation": "study",
            "target": "lastupdate",
            "targetKey": "study_ID",
            "sourceKey": "lastUpdate_ID",
            "keysIn": "study",
            "targetStorageType": "sql"
        },
        "location": {
            "type": "many_to_one",
            "implementation": "foreignkeys",
            "reverseAssociation": "studies",
            "target": "location",
            "targetKey": "studies_IDs",
            "sourceKey": "location_ID",
            "keysIn": "study",
            "targetStorageType": "sql"
        },
        "observationLevels": {
            "type": "one_to_many",
            "implementation": "foreignkeys",
            "reverseAssociation": "study",
            "target": "observationunithierarchylevel",
            "targetKey": "study_ID",
            "sourceKey": "observationLevels_IDs",
            "keysIn": "study",
            "targetStorageType": "sql"
        },
        "observationVariables": {
            "type": "many_to_many",
            "implementation": "foreignkeys",
            "reverseAssociation": "studies",
            "target": "observationvariable",
            "targetKey": "studies_IDs",
            "sourceKey": "observationVariables_IDs",
            "keysIn": "study",
            "targetStorageType": "sql"
        },
        "trial": {
            "type": "many_to_one",
            "implementation": "foreignkeys",
            "reverseAssociation": "studies",
            "target": "trial",
            "targetKey": "studies_IDs",
            "sourceKey": "trial_ID",
            "keysIn": "study",
            "targetStorageType": "sql"
        },
        "callSets": {
            "type": "one_to_many",
            "implementation": "foreignkeys",
            "reverseAssociation": "study",
            "target": "callset",
            "targetKey": "study_ID",
            "sourceKey": "callSets_IDs",
            "keysIn": "study",
            "targetStorageType": "sql"
        },
        "plates": {
            "type": "one_to_many",
            "implementation": "foreignkeys",
            "reverseAssociation": "study",
            "target": "plate",
            "targetKey": "study_ID",
            "sourceKey": "plates_IDs",
            "keysIn": "study",
            "targetStorageType": "sql"
        },
        "samples": {
            "type": "one_to_many",
            "implementation": "foreignkeys",
            "reverseAssociation": "study",
            "target": "sample",
            "targetKey": "study_ID",
            "sourceKey": "samples_IDs",
            "keysIn": "study",
            "targetStorageType": "sql"
        },
        "variantSets": {
            "type": "one_to_many",
            "implementation": "foreignkeys",
            "reverseAssociation": "study",
            "target": "variantset",
            "targetKey": "study_ID",
            "sourceKey": "variantSets_IDs",
            "keysIn": "study",
            "targetStorageType": "sql"
        },
        "events": {
            "type": "many_to_many",
            "implementation": "foreignkeys",
            "reverseAssociation": "study",
            "target": "event",
            "targetKey": "study_IDs",
            "sourceKey": "events_IDs",
            "keysIn": "study",
            "targetStorageType": "sql"
        },
        "observations": {
            "type": "one_to_many",
            "implementation": "foreignkeys",
            "reverseAssociation": "study",
            "target": "observation",
            "targetKey": "study_ID",
            "sourceKey": "observations_IDs",
            "keysIn": "study",
            "targetStorageType": "sql"
        },
        "observationUnits": {
            "type": "one_to_many",
            "implementation": "foreignkeys",
            "reverseAssociation": "study",
            "target": "observationunit",
            "targetKey": "study_ID",
            "sourceKey": "observationUnits_IDs",
            "keysIn": "study",
            "targetStorageType": "sql"
        }
    },
    "internalId": "studyDbId"
}
```

</details>

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
        "commonCropName": {
            "type": "String",
            "description": "Common name for the crop associated with this study"
        },
        [...]
    }
}
```
As you can see, the primary key (here `study_github_ID`) contains the custom primary key name `github` and the data type is Integer.
Each generated data model contains the custom primary key name and is of the specified type.

---

#### Associations

All associations/relationships are defined after Zendro's [paired-end foreign keys](https://zendro-dev.github.io/setup_root/data_models#paired-end-foreign-keys).

---

## Program Workflow

### Main Execution (`main()`)

This is the main function of the script.<br />
Calls functions to locate JSON schema files, extract models, process their properties, and generate output files.

---

### File Handling (`get_files(input_path)`)

Recursively searches the input directory for .json files and returns a list of valid file paths.

---

### Model Extraction (`get_models(input_files)`)

- Reads JSON files and extracts models from the `$defs` section.
- Filters out incompatible models, such as `enum` types.
- Stores model attributes, associations, and primary keys in dictionaries.

---

### Property Conversion (`get_properties(models)`)

- Converts BrAPI properties into Zendro-compatible attributes and associations.
- Determines primary key settings based on user input or schema patterns (´DbId´).
- Handles ´oneOf´ and ´allOf´ definitions by integrating properties from referenced models.

---

### Association Handling (`get_reverse_association(association)`)

- Maps BrAPI relationship types (´one-to-many´, ´many-to-one´, etc.) to Zendro format (´one_to_many´, ´many_to_one´, etc).
- Ensures, that bidirectional associations are properly defined.

---

### Property Type Conversion (`get_property_type(input_property)`)

- Matches BrAPI types (´string´, ´integer´, ´boolean´, ´number´) with Zendro-compatible types (´String´, ´Int´, ´Boolean´, ´Float´).
- Supports array definitions (and nested properties).

---

### Output Generation (`write_json(output_models)`)

- Formats converted models into JSON files with a standard Zendro structure.
- Saves the files in the specified output directory.

---

### Logging (`log(msg)`)

Logs errors and warnings in ´Log.txt´, recording timestamps.

---

## Error Handling

- Uses ´try-except´ blocks to catch file access errors (´OSError´), JSON parsing errors, and unexpected exceptions.
- Logs relevant information to ´Log.txt´ for debugging (including timestamp)
- Exits program in case of critical failures using ´sys.exit(1)´.

---

## Notes

- Excludes models with unsopported types (e.g. enum).
- Handles ´oneOf´ properties interactively, prompting user input.
- Supports multiple storage backends with configurable options.

---

## Possible Improvements

- Automatic handling of ´oneOf´ properties without user input. <br /> This can be implemented, for example, by using command line arguments to decide in advance whether the program should select automatically or whether user input should be required.
- Enhanced error reporting with detailed exception tracking.
