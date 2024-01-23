from DbfReader import DBFReader
from BerlinTime import BerlinTime
import pandas as pd
import math
import os

# fmt:off

class OutputDataframe:
    def __init__(self) -> None:
        pass

    def get_final_dataframe(self, files):
        self.df = pd.DataFrame()
        self.dataframes = {} # Converted tables to dataframe results
        self.tables = {} # Dict of file names and tables content "Name of file" : "Dataframe"
        self.file_names = [] # Sorted file names
        self.files = files # Iported files path
        self.files_dict = {os.path.basename(f): f for f in self.files} # Dictionary of files "Name" : "Path"
        time = BerlinTime()

        if self._find_key_file(self.files_dict) != None: # If "IqRfSvr.dbf" - key file found
            svr = DBFReader(self._find_key_file(self.files_dict))
            svr_df = svr.readData()
            self.files_dict.pop("IqRfSvr.dbf")

             # Create Dataframes from all files
            for name, path in self.files_dict.items():
                f = DBFReader(path)
                self.tables[name] = f.readData()
                self.file_names.append(name)

            for name, data_df in self.tables.items():
                T = data_df.at[0, "VALUE"]
                data_df['TIMESTAMP'] = data_df['VALUE'].where(data_df['TAGID'] == '*t').ffill()

                # Reformatting to wide format
                table = data_df.pivot_table(index='TIMESTAMP', columns='TAGID', values='VALUE', aggfunc='first')

                # Replace None values with the previous value in the same column (except the "*T" column)
                table = table.apply(lambda column: column.ffill() if column.name != '*T' else column)

                # Reset index
                table.reset_index(inplace=True)

                # Calculating real timestamps
                table['TIMESTAMP'] = table['TIMESTAMP'].apply(lambda x: time.getTime(T,x) if not math.isnan(x) else None)

                # Creating sensor ID and names DICT
                sensors = dict(zip(list(svr_df["ID"]), list(svr_df["NAME"])))
                sensors_res = dict(zip(list(svr_df["NAME"]), list(svr_df["K"])))
                sensors_res2 = dict(zip(list(svr_df["NAME"]), list(svr_df["Q"])))

                # Rename Sensor ID names
                for i in table.columns:
                    if i in sensors:
                        table = table.rename(columns={i: sensors[i]})

                # Calculating real values
                for i in table.columns:
                    if i in sensors_res:
                        #print(i)
                        table[i] = table[i].apply(lambda x: abs(round(float(x) * sensors_res[i]+sensors_res2[i],3)) if isinstance(x, (float, int)) or (isinstance(x, str) and x.replace('.', '', 1).isdigit()) else None)

                # Remove 'nan' values from table
                table = table.fillna('')
                self.dataframes[name] = table
            
            for i in self.dataframes.values():
                self.df = pd.concat([self.df, i])

            # Remove junk columns
            if "*N" in self.df.columns:
                del self.df['*N']

            # Remove junk columns
            if "*T" in self.df.columns:
                del self.df['*T']

            # Remove junk columns
            if "*t" in self.df.columns:
                del self.df['*t']

            # Remove TAGID index column from Index data
            self.df.rename_axis(None, axis=1, inplace=True)
            return self.df
            
        else:
            # Create Dataframes from all files
            for name, path in self.files_dict.items():
                f = DBFReader(path)
                self.tables[name] = f.readData()
                self.file_names.append(name)

            # Concating all Dataframes in one
            for i in range(len(self.file_names)):
                if len(self.file_names) > 0:
                    self.df = pd.concat([self.df, self.tables[self.file_names[i]]])
            #print(self.df)
            return self.df

                
    # Find "IqRfSvr.dbf" if exist
    def _find_key_file(self,files):
        self.files = files
        if "IqRfSvr.dbf" in self.files.keys():
            return self.files["IqRfSvr.dbf"]
        else:
            return None
