import pandas as pd

class JsonToExcelConverter:
    """
    A class to convert a JSON file to an Excel file.
    """

    def __init__(self, input_json_file: str, output_excel_file: str):
        """
        Initialize with the input JSON file path and the output Excel file path.
        
        :param input_json_file: Path to the input JSON file.
        :param output_excel_file: Path to the output Excel file.
        """
        self.input_json_file = input_json_file
        self.output_excel_file = output_excel_file

    def convert(self):
        """
        Convert the JSON file to an Excel file.
        """
        try:
            data = pd.read_json(self.input_json_file)
            data.to_excel(self.output_excel_file, index=False)
            print(f"Conversion successful. Excel file saved to {self.output_excel_file}")

        except ValueError as e:
            print(f"Error reading JSON file: {e}")
        except Exception as e:
            print(f"An error occurred during the conversion: {e}")
if __name__ == "__main__":
    # Example usage
    converter = JsonToExcelConverter(r"C:\Users\Shashwat.Sharma\Documents\Mokshayani\AcademiaAssistant\Summary\Deepti Mehrotra_publications.json", "output.xlsx")
    converter.convert()
