class DBFHeaderParser:
    def __init__(self, hex_head):
        self.hex_representation = hex_head

        self.extract_information()

    # fmt: off
    def extract_information(self):

        # create a byte array from the hexadecimal string for both parts
        self.header_bytes = bytes.fromhex(self.hex_representation)

        # Zero byte - DBF version
        self.version = self.header_bytes[0]

        # First byte - year of file creation
        self.year = 1900 + self.header_bytes[1]

        # Second byte - month of file creation
        self.month = self.header_bytes[2]

        # Third byte - day of file creation
        self.day = self.header_bytes[3]

        # 4-7 byte - number of records
        self.record_count = int.from_bytes(self.header_bytes[4:8], byteorder="little")

        # Number of bytes in the header
        self.bytes_in_header = int.from_bytes(
            self.header_bytes[8:10], byteorder="little"
        )

        # Number of bytes in the record
        self.bytes_in_records = int.from_bytes(self.header_bytes[10:12], byteorder="little")

    def get_headers(self) -> dict:
        headers = {}
        name = []
        headerType = []
        headerLen = []

        # Get information about each header name
        for header_column in range(32, len(self.header_bytes), 32):
            name.append((self.header_bytes[header_column : header_column + 9].decode("ascii")).replace('\x00', ''))

        # Get information about each header type
        for header_type in range(32+11, len(self.header_bytes), 32):
            headerType.append((self.header_bytes[header_type:header_type+1].decode("ascii")).replace('\x00', ''))

        # Make list with header NAME:TYPE (ex.: ID:I)
        header_list = [f"{n}:{t}" for n, t in zip(name, headerType)]

        # Get information about each header size
        for header_len in range(48, len(self.header_bytes),32):
            hex_value = self.header_bytes[header_len:header_len+1].hex()
            headerLen.append(int(hex_value, 16))
            
        headers = dict(zip(header_list, headerLen))

        return headers
    
    def get_dbf_info(self) -> dict:
        info = {}
        info["version"] = self.version
        info["year"] = self.year
        info["month"] = self.month
        info["day"] = self.day
        info["records"] = self.record_count
        info["header_bytes"] = self.bytes_in_header
        info["record_bytes"] = self.bytes_in_records

        return info
    # fmt: on
