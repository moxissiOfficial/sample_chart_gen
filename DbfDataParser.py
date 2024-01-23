# fmt:off
import struct
import pandas as pd

class DBFDataParser:
    def __init__(self, dbf_info, header, hex_body) -> None:
        self.dbf_info = dbf_info
        self.header = header
        self.hex_body = bytes.fromhex(str(hex_body))
        self.data = {}

    def read_data(self) -> pd.DataFrame:
        position = 2 # Start Position of calculating bytes
        for head, size in self.header.items():
            if ":I" in head:
                self.data[head.replace(":I","")] = []
                for data_position in range(position, len(self.hex_body), self.dbf_info["record_bytes"]):
                    value = (self.hex_body[data_position : data_position + size]).hex()
                    if value[0] == "0":
                        self.data[head.replace(":I","")].append("")
                    else:
                        self.data[head.replace(":I","")].append(self.hex_to_decimal(value))
            elif ":C" in head:
                self.data[head.replace(":C","")] = []
                for data_position in range(position, len(self.hex_body), self.dbf_info["record_bytes"]):
                    value = (self.hex_body[data_position : data_position + size]).strip()
                    if value == b'':
                        self.data[head.replace(":C","")].append("")
                    elif len(value) == 3:
                        self.data[head.replace(":C","")].append(self.decode_ID(value.decode('latin-1')))
                    else:
                        self.data[head.replace(":C","")].append(value.decode('latin-1').replace("ø","°"))
            elif ":O" in head:
                self.data[head.replace(":O","")] = []
                for data_position in range(position, len(self.hex_body), self.dbf_info["record_bytes"]):
                    value = (self.hex_body[data_position : data_position + size])
                    double_value = struct.unpack('>d', value)[0]
                    abs_float_value = abs(double_value)
                    if value[0] == 0:
                        self.data[head.replace(":O","")].append("")
                    else:
                        self.data[head.replace(":O","")].append(abs_float_value)

            elif ":W" in head:
                self.data[head.replace(":W","")] = []
                for data_position in range(position, len(self.hex_body), self.dbf_info["record_bytes"]):
                    value = (self.hex_body[data_position : data_position + size]).strip()#.replace(b'', '')
                    self.data[head.replace(":W","")].append(value.decode('latin-1').replace('\x00', '').replace(' ', ''))
            position += size
        df = pd.DataFrame(self.data)
        return df

    def hex_to_decimal(self, hex_value):
        decimal_value = int(hex_value, 16)

        #Invert highest bite in first byte
        decimal_value ^= 1 << (len(hex_value) * 4 - 1)

        if decimal_value & (1 << (len(hex_value) * 4 - 1)):
            decimal_value -= 1 << (len(hex_value) * 4)
        return decimal_value

    def decode_ID(self, id):
        base_64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
        decoded_id = []
        for i in range(0, 3):
            decoded_id.append(base_64.index(id[i]))
        result = (decoded_id[0] << 12) + (decoded_id[1] << 6) + decoded_id[2]
        return result
