import sys
import MySQLdb 
from datetime import date, datetime
import re

class Database:
    """
    This class is for loading
    """
    def __init__(self, conf_file):
        self.open_conf(conf_file)
        self.cnx = MySQLdb.connect(user=self.db_user, db=self.db_name, passwd=self.db_password)
        self.cursor = self.cnx.cursor()

    def open_conf(self, file_name):
        with open(file_name, 'r') as c:
            for line in c.readlines():
                char_pos = line.find("=")
                if line.startswith("USER"):
                    self.db_user = line[char_pos+1:].strip()
                if line.startswith("PASSWORD"): 
                    self.db_password = line[char_pos+1:].strip()
                if line.startswith("DBNAME"): 
                    self.db_name = line[char_pos+1:].strip()
                if line.startswith("HOST"): 
                    self.host = line[char_pos+1:].strip()


    def load(self, tokenized_data, S):
        count = 0
        for row in tokenized_data:
            data_restaurant = (row[(S.s["CAMIS"])], row[(S.s["DBA"])], row[(S.s["CUISINE"])], \
                               row[(S.s["BUILDING"])], row[(S.s["STREET"])], row[(S.s["BORO"])], \
                               row[(S.s["ZIPCODE"])], row[(S.s["PHONE"])], row[(S.s["FULL_ADDRESS"])],)
            #print 'data rest ', data_restaurant
            data_inspection = (row[(S.s["CAMIS"])], row[(S.s["INSPECTION_TYPE"])], \
                               row[(S.s["INSPECTION_DATE"])], row[(S.s["SCORE"])], \
                               row[(S.s["ACTION"])], row[(S.s["GRADE"])], \
                               row[(S.s["GRADE_DATE"])], row[(S.s["VIOLATION_CODE"])] ) 
            data_violation = (row[(S.s["VIOLATION_CODE"])], row[(S.s["DESCRIPTION"])], \
                              row[(S.s["CRITICAL_FLAG"])] ) 
            count = count + 1
            self.cursor.execute ("""
                INSERT INTO restaurant 
                (camis, dba, cuisine, building, street, boro, zipcode, phone, full_address)
                VALUES 
                (%s, %s, %s, %s, %s, %s, %s, %s, %s) 
                ON DUPLICATE KEY UPDATE 
                dba  = VALUES(dba);
                """, data_restaurant) 

            self.cursor.execute ("""
                INSERT INTO inspection 
                (camis, inspection_type, inspection_date, score, action, grade, grade_date, violation_code)
                VALUES 
                (%s, %s, %s, %s, %s, %s, %s, %s); 
                """, data_inspection)

            self.cursor.execute ("""
                INSERT INTO violation 
                (violation_code, description, critical_flag)
                VALUES 
                (%s, %s, %s) 
                ON DUPLICATE KEY UPDATE 
                description  = VALUES(description),
                critical_flag = VALUES(critical_flag);
                """, data_violation)

        self.cnx.commit()
        self.cnx.close()


class InputSchema:
    def __init__(self, in_schema_file, in_has_header, in_delims):
        self.schema_source = in_schema_file
        self.has_header = in_has_header
        self.delims = in_delims
        self.s = {}
        self.num_cols = -1
        self.load_schema()

    def load_schema(self): 
        with open(self.schema_source, 'r') as s:
            for count, line in enumerate(s.readlines()):
               self.s[line.strip()] = count 
        self.num_cols = len(self.s)
        # Add additioal paramters
        self.s['FULL_ADDRESS'] = self.num_cols 


class Data:
    """
    This class is for Extracting and Transforming input data
    """

    def __init__(self, in_data, input_schema):
        self.source_file = in_data
        self.tokenized_data = []
        self.load_data(in_data, input_schema)


    def load_data(self, in_data, S):
        with open(in_data, 'r') as f:
            lines = f.readlines()
            if input_schema.has_header:
                lines = lines[1:]
            count = 0
            for line in lines:
                count = count + 1
                tokens = []
                tokens = [x.strip() for x in line.split(',')]
                if len(tokens) != S.num_cols:
                    is_valid, new_line = self.clean_line(line, S.delims)
                    print 'CHANGED --> ', new_line
                    if is_valid == False:
                        print "CRIT: COLUMN NUMBER IS ", S.num_cols, " NOT ", len(tokens)
                        continue
                    else:
                        tokens = new_line.split(',')
                tokens = self.convert_date(tokens, S)
                tokens = self.clean_cuisine(tokens, S)
                col = 0
                tokens = self.add_full_address(tokens, S)                
                self.pretty_print(tokens, line, S)
                self.tokenized_data.append(tokens)

    def strip_non_ascii(self,text):
        """ Returns the text without non ASCII characters """
        stripped = (c for c in text if 0 < ord(c) < 127)
        return ''.join(stripped)


    def convert_date(self, tokens, S):
        if tokens[(S.s["GRADE_DATE"])]:
            tokens[(S.s["GRADE_DATE"])] = datetime.strptime(tokens[(S.s["GRADE_DATE"])], '%m/%d/%Y')
        else:
            tokens[(S.s["GRADE_DATE"])] = ""  
        if tokens[(S.s["INSPECTION_DATE"])]:
            tokens[(S.s["INSPECTION_DATE"])] = datetime.strptime(tokens[(S.s["INSPECTION_DATE"])], '%m/%d/%Y')
        else:
            tokens[(S.s["INSPECTION_DATE"])] = "" 
        if tokens[(S.s["RECORD_DATE"])]:
            tokens[(S.s["RECORD_DATE"])] = datetime.strptime(tokens[(S.s["RECORD_DATE"])], '%m/%d/%Y')
        else:
            tokens[(S.s["RECORD_DATE"])] = ""
        return tokens 

    def clean_cuisine(self, tokens, S):
        # Flatten ASCII
        # Remove additional description in (...), the regex below only searches for the first one found (need to change)
        if tokens[(S.s["CUISINE"])]:
            print  tokens[(S.s["CUISINE"])]
            new_cuisine = self.strip_non_ascii(tokens[(S.s["CUISINE"])])
            m = re.finditer(r"\([^\)]+\)", new_cuisine)
            start = -1
            for iterm in m:
                start = iterm.start(0)
                if start > 0:
                    tokens[(S.s["CUISINE"])] = (new_cuisine[:start]).replace("&", "and").replace("\"", "")
                    break 
            if start == -1:
                tokens[(S.s["CUISINE"])] = new_cuisine.replace("&", "and").strip("\"")
        else:
           # standard text in the data
           tokens[(S.s["CUISINE"])] = "Not Listed/Not Applicable" 
        return tokens
        # Remove Non-alphanumeric


    def add_full_address(self, tokens, S):
        full_address = tokens[(S.s["BUILDING"])].strip() + " " + tokens[(S.s["STREET"])].strip() \
                     + " " + tokens[(S.s["BORO"])].strip() + " " + tokens[(S.s["ZIPCODE"])].strip()
        tokens.append(full_address)
        return tokens

    def clean_line(self,line, delim):
        delim_index =  [pos for pos, char in enumerate(line) if char == delim]
        valid = True
        if len(delim_index) == 0:
            return line
        if len(delim_index) > 0 and len(delim_index) % 2 == 0:
            start = 0
            new_line = ""
            for i in range(0, len(delim_index), 2):
            #for i, pos in enumerate(delim_index):
                d_start = delim_index[i]
                d_end = delim_index[i+1]
                new_line = new_line + line[start:d_start]
                convert_line = line[d_start:d_end+1]
                convert_line = convert_line.replace(",", " ")
                new_line = new_line + convert_line
                start = d_end
            if start < len(line):
                new_line = new_line + line[start+1:]
            return (True, new_line)
        else:
            return (False, line)    


    def pretty_print(self, tokens, line, S):
       print "-- ORG LINE -- ", line
       print "1 - CAMIS ", tokens[0] 
       print "2 - DBA ", tokens[1] 
       print "3 - BORO ", tokens[2]
       print "4 - BUILDING ", tokens[3]
       print "5 - STREET ", tokens[4]
       print "6 - ZIPCODE ", tokens[5]
       print "7 - PHONE ", tokens[6]
       print "8 - CUISINE ", tokens[7]
       print "9 - INSPECTION_DATE ", tokens[8]
       print "10 - ACTION ", tokens[9]
       print "11 - VIOLATION_CODE ", tokens[10]
       print "12 - DESCRIPTION ", tokens[11]
       print "13 - CRITICAL_FLAG ", tokens[12]
       print "14 - SCORE ", tokens[13]
       print "15 - GRADE ", tokens[14]
       print "16 - GRADE_DATE ", tokens[15]
       print "17 - RECORD_DATE ", tokens[16]
       print "18 - INSPECTION_TYPE ", tokens[17]
       if len(tokens) == 19:
           print "19 - FULL ADDRESS ", tokens[18]

if __name__ == "__main__":
    args = sys.argv
    delims = "\""
    input_schema = InputSchema(args[1], True, delims)
    database = Database(args[2])
    cleaned_data = Data(args[3], input_schema)
    print 'before load '
    database.load(cleaned_data.tokenized_data, input_schema)
    print 'after load '
