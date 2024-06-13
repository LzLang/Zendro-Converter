import os
import sys
import json
from datetime import datetime, date


class DataModelConverter:
    def __init__(self, input_path):
        self.__models = {}
        self.__input_files = self.__get_files(input_path)
        input_files_models = self.__get_models()

        self.__get_properties(input_files_models)

        self.__files_date = {}
        self.__models = {}

        self.__get_files(input_path)
        self.__get_files_models(__input_files)

    def __get_files(self, input_path):
        try:
            input_files = []

            for root, directories, files in os.walk(input_path):
                for filename in files:
                    # Only json files are needed
                    if os.path.splitext(filename)[1].lower() == '.json':
                        # Append the file
                        file_path = os.path.join(root, filename)
                        input_files.append(file_path)

            return input_files
        except:
            print("Test")

    def __get_models(self):
        try:
            files_data = {}
            for file in self.__input_files:
                with open(file, "r") as open_file:
                    models = json.load(open_file)['$defs']
                    for current_model in models:
                        files_data[current_model] = {}
                        self.__models[current_model] = {}
                        files_data[current_model]['properties'] = models[current_model]['properties']
                        files_data[current_model]['required'] = models[current_model]['required']

            return files_data if files_data else None

        except OSError as file_error:
            self.log(f"Couldn't open files: {file_error}")
        except Exception as model_exception:
            print(model_exception)
            self.log(f"An error occurred: {model_exception}")
            sys.exit(1)

    def __get_properties(self, input_files_models):


    @staticmethod
    def log(msg):
        """
        Writes the message to a log-file.\n
        Logs the date and time automatically.

        :param msg: Message to log
        """

        try:
            # Get current date and time and write this with the message to the log file
            with open("Log.txt", "a") as file:
                current_time = datetime.now().strftime("%H:%M:%S")
                file.write(f"{str(date.today())} - {current_time}:\t{msg}\n")
                print(f"An error occurred, please view the log file for details!")
        except OSError as log_error:
            # Prints the occurred error
            print(f"An error occurred while writing the log file: {log_error}")
