import os
import sys
sensitive = {"password", "secret", "key", "token", "api"}       
          
        


def inside_comment(string):
    # cheking the presence if comments in the value strings and returning them f found
    value =""
    comment = ""
    in_quote = False 
    idx = None
    for i , char in enumerate(string) :
         
        if char in ("'", '"') and in_quote == False :
            
            in_quote = True 
        else :
                if char in ("'", '"')  and in_quote == True:
                    in_quote = False 
                    
        
        if char == "#" and not in_quote :
              idx = i 
              value = string[:idx]
              comment = string[idx+1:]
              break 
    if idx is not None  :
         value = string[:idx]
         comment = string[idx+1:]
    else :
         value = string 
         comment = ""
    
    return value , comment



        

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
                

def sort_type(line):#this function aims to convert each string to its actual type 
    if not line :
        return ""
    else :
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
        return True 
    else :
        return False 


def read_and_parse (file_path):
    """
this function will read the file line by line and parse the data as comments pairs of key and values skipping empty lines
"""
    data_parse = {}
    comment= {}
    if not file_check (file_path):
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
                        value , nested_comment = inside_comment(value)
                        value = sort_type(value.strip())
                        if value == "" :
                            data_parse [key] = f"missing value by line {idx+1}"
                        else :
                            data_parse [key] = value

                        if  nested_comment :
                            comment [f"extracted comment {idx+1}"] = nested_comment
            return data_parse , comment   
        

def load (dic):
    for key , value in dic.items():
        os.environ[key] = str(value)


def mask (string):
    if len(string) <= 4 :
        return "*" * len(string)
    return string[:4] + "*" * (len(string)-4)


def is_sensitive(key):
     #find common values that wwe want to be masked while treating few edge cases such as monkey
    parts = key.lower().split("_")
    return any(part in sensitive for part in parts)


def get(key, default=None ,masked = False):
    value = os.environ.get(key, default)
    if is_sensitive(key) or masked :
        return mask(str(value))
    return value



def load_env(file_path): # take the parsed values from the read and parse function and load them in teh env 
    data , comment = read_and_parse(file_path)
    load (data)

def require(key_list) :
    
    catched_error = {}

    for key in key_list:
        if key not in os.environ:
            catched_error[key] = f"missing required key: {key}"

    if catched_error:
        for msg in catched_error.values():

            print(f"{msg}")   
        sys.exit(1)

    print("all keys have been successfully tested")


def write(data):
    parsed_list = []
    for key , value in data.items():
        parsed_list.append(f"{key}={value}\n")
    return parsed_list


def write_env(file_path , data , overwrite=False):
    # load the vparsed data from read_and_parse in a new file
    if not data :
        return None 
    if file_check(file_path) and not overwrite :
        print (f"this file {file_path} already exists")
        return None
    with open (file_path,"w") as f :
        L = write(data)
        f.writelines(L)
    return True 



    

       

    

        

            


         


if __name__ == "__main__":
    load_env(".env")
    