import pandas as pd
from DbfHeaderParser import DBFHeaderParser
from DbfDataParser import DBFDataParser


class DBFReader:
    def __init__(self, file_path: str):
        self._file_path = file_path

    def readData(self) -> pd.DataFrame:
        self._read_dbf_file()
        header_parser = DBFHeaderParser(self.header)
        body_parser = DBFDataParser(
            header_parser.get_dbf_info(), header_parser.get_headers(), self.body
        )
        return body_parser.read_data()

    def _read_dbf_file(self):
        with open(self._file_path, "rb") as file:
            # Read file contents as binary data
            binary_data = file.read()

            # Convert binary data to hexadecimal string with line breaks
            hex_representation = ""
            for i, byte in enumerate(binary_data):
                hex_representation += format(byte, "02X") + " "

                # Line break every 16 bytes
                if (i + 1) % 16 == 0:
                    hex_representation += "\n"

            # We find position "0D"
            index_0D = hex_representation.find("0D")

            # Split the hexadecimal string into two parts
            self.header = hex_representation[:index_0D]
            self.body = hex_representation[index_0D:]

    def _get_header_and_body(self):
        return self.header, self.body
