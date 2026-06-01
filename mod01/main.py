import os

def is_int (string):
    try :
        int(string)
        return True 
    except ValueError :
        return False 
def is_float (string):
    try:
        float (string)
        return True 
    except ValueError :
        return False 
                

def sort_type(line):#this function aims t convert each string to its actual type 
    
    if line.lower() == "true":
        return True 
    elif line.lower() == "false":
        return False 
    elif line.startswith("'") and line.endswith("'") or line.startswith('"') and line.endswith('"'):
        return line[1:-1]
    elif is_int(line):
        return int(line) 
    elif is_float (line):
        return float(line) 
    else :
        return line 

def file_check(file_path):# check file existence 
    if os.path.exists(file_path):
        print(f"{file_path} does exist ")
        return True 
    else :
        print (f"{file_path} does not exist ")
        return False 

"""
this function will read the file line by line and parse the data as comments pairs of key and values skipping empty lines
"""
def read_and_parse (file_path):
    data_parse = {}
    comment= {}
    if not file_check (file_path):
        print("File not found. Exiting.")
        return None
    else :
        with open (file_path , "r") as f :
            for idx , line in enumerate(f) :
                line = line.strip()
                if not line  :
                    continue 

                elif line.startswith("#"):
                    comment [f"line {idx+1}"] = line 
                else :
                    if "=" in line :
                        key , value = line.split("=",1)
                        key = key.strip()
                        value = sort_type(value.strip())
                        data_parse [key] = value
            print ("comments:",comment)
            print ("key found:",data_parse)
            return data_parse , comment   

                

         





    


if __name__ == "__main__" :
    read_and_parse(".env")
    
