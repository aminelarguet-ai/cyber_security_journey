from abc import ABC, abstractmethod
import boto3


class SecretProvider(ABC):
    @abstractmethod
    def get_secret(self, secretId):
        pass 
        



class AWSSecretProvider(SecretProvider):
    def __init__(self, client):
        super().__init__()
        self.client = client 

    def get_secret(self):
        response = self.client.get_secret_value(SecretId="my-app/api-key")
        secret = response["SecretString"]
        



    