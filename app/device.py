from loguru import logger

class Device:
    name: str
    id:str
    access_token: str

    
    def __init__(self,name:str,id: str, access_token:str):
        self.ip = name
        self.id = id
        self.access_token = access_token
    
