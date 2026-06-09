import os ,sys


class EnvParser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = {}
        self.comments = {}

    def _is_int(self, string):
         try:
           int(string)
           return True
         except (ValueError, TypeError):
          return False

    
    def _is_float(self, string): 
           try:
            float (string)
            return True 
           except ValueError :
            return False 
                
    def _sort_type(self, line):
        if not line :
         return ""
        else :
         if line.lower() == "true":
            return True 
         elif line.lower() == "false":
            return False 
         elif line.startswith("'") and line.endswith("'") or line.startswith('"') and line.endswith('"'):
            return line[1:-1]
         elif self._is_int(line):
            return int(line) 
         elif self._is_float(line):
            return float(line) 
         else :
            return line
    def _inside_comment(self, string): 
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

       
    def _expand(self): 
           
           if not self.data:
            return None

           for key in list(self.data.keys()):
                value = str(self.data[key])

                seen_states = set()  

                while "${" in value:
                    if value in seen_states:
                        print(f"Circular reference detected while expanding '{key}'")
                        break

                    seen_states.add(value)

                    start = value.find("${")
                    end = value.find("}", start)

                    if end == -1:
                        break

                    var = value[start + 2:end]

                    replacement = str(self.data.get(var, f"${{{var}}}"))

                    value = value[:start] + replacement + value[end + 1:]

                self.data[key] = self._sort_type(value)

           return self.data 
    def parse(self): 
        """
        this function will read the file line by line and parse the data as comments pairs of key and values skipping empty lines
            """
        if not  os.path.exists(self.file_path):
            return None
            
        else :
            with open (self.file_path , "r") as f :
                for idx , line in enumerate(f) :
                    line = line.strip()
                    if not line  :
                        continue 

                    elif line.startswith("#"):
                        self.comments [f"line {idx+1}"] = line 
                    else :
                        if "=" in line :
                            key , value = line.split("=",1)
                            key = key.strip()
                            value , nested_comment = self._inside_comment(value)
                            value = self._sort_type(value.strip())
                            if value == "" :
                                self.data [key] = f"missing value by line {idx+1}"
                            else :
                                self.data[key] = value

                            if  nested_comment :
                                self.comments [f"extracted comment {idx+1}"] = nested_comment
                self._expand()
        


class EnvStore:
    SENSITIVE = {"password", "secret", "key", "token", "api"}

    def __init__(self):
        self._store = {}

    def load(self, data):
        for key , value in data.items():
         self._store[key] = str(value)

    def get(self, key, default=None, masked=False): 
        value = self._store.get(key, default)
        if self._is_sensitive(key) or masked :
            return self._mask(str(value))
        return value
    def require(self, key_list): 
            catched_error = {}

            for key in key_list:
                if key not in self._store:
                    catched_error[key] = f"missing required key: {key}"

            if catched_error:
                for msg in catched_error.values():

                    print(f"{msg}")   
                raise ValueError(f"Missing required keys: {list(catched_error.keys())}")
            print("all keys have been successfully tested")

    def _mask(self, string): 
            if len(string) <= 4 :
             return "*" * len(string)
            return string[:4] + "*" * (len(string)-4)

    def _is_sensitive(self, key): 
             #find common values that wwe want to be masked while treating few edge cases such as monkey
        parts = key.lower().split("_")
        return any(part in self.SENSITIVE for part in parts)



class EnvFile:
    def __init__(self, file_path):
        self.file_path = file_path

    def exists(self): 
        if os.path.exists(self.file_path):
         return True 
        else :
         return False 
        
    def _format(self, data):
       return [f"{key}={value}\n" for key, value in data.items()]
 
    def write(self, data, overwrite=False):
        if not data:
            return None
        if self.exists() and not overwrite:
            print(f"this file {self.file_path} already exists")
            return None

        lines = self._format(data)

        with open(self.file_path, "w") as f:
            f.writelines(lines)

        return True


if __name__ == "__main__":
    def __init__(self, file_path=None):

        parser = EnvParser(".env")
        parser.parse()

    def load(self, file_path):
        store = EnvStore()
        store.load(parser.data)

    def require (self ,list):
        store.require(["DATABASE_URL", "API_KEY"])

    # 4. Get a value
    print(store.get("API_KEY"))

    # 5. Write to a new file
    env_file = EnvFile(".env.backup")
    env_file.write(parser.data)