
import pandas as pd
import json
import excel2json
class ExcelToJsonConverter:
    """
    A class to convert an Excel file to a JSON file.
    """

    def __init__(self, input_excel_file: str, output_json_file: str, sheet_name: str = 'sheet1', engine: str = None):
        """
        Initialize with the input Excel file path, the output JSON file path, and sheet name.
        
        :param input_excel_file: Path to the input Excel file.
        :param output_json_file: Path to the output JSON file.
        :param sheet_name: Name of the Excel sheet to read from. Defaults to 'sheet1'.
        :param engine: The engine to use for reading the Excel file. Use 'openpyxl' for .xlsx files and 'xlrd' for .xls.
        """
        self.input_excel_file = input_excel_file
        self.output_json_file = output_json_file
        self.sheet_name = sheet_name
        self.engine = engine

    def convert(self):
        """
        Convert the Excel file to JSON format and write the output to the specified JSON file.
        """
        try:
            # Read the Excel file, specifying the engine if necessary
            excel_data_df = pd.read_excel(self.input_excel_file, sheet_name=self.sheet_name, engine=self.engine)
            
            # Convert the Excel data to JSON string (list of records)
            json_data = excel_data_df.to_json(orient='records')
            
            # Convert JSON string to Python dictionary (list of records)
            json_data_dict = json.loads(json_data)
            
            # Write the data to the JSON file
            with open(self.output_json_file, 'w', encoding='utf-8') as json_file:
                json.dump(json_data_dict, json_file, indent=4)
            
            print(f"Conversion successful. JSON data saved to {self.output_json_file}")
        
        except FileNotFoundError as e:
            print(f"Error: {e}")
        except ValueError as e:
            print(f"Error reading the Excel file: {e}")
        except Exception as e:
            print(f"An error occurred during conversion: {e}")
    
    def convert2(self):
        path_excel = self.input_excel_file
        df = pd.read_excel(path_excel, engine='openpyxl')
        json_data = df.to_json(orient='records', indent=4)
        print(json_data)
        path_json = 'final_result.json'
        with open(path_json, 'w') as json_file:
            json_file.write(json_data)
if __name__ == "__main__":
    # Example usage of the ExcelToJsonConverter class
    converter = ExcelToJsonConverter(input_excel_file=r"C:\Users\Shashwat.Sharma\Downloads\Final Selected- ISRO Immersion Challenge.xlsx", output_json_file='data.json', sheet_name='sheet1', engine='openpyxl')
    converter.convert2()
