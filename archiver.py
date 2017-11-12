import boto3
from botocore.vendored import requests
import os

DOWNLOAD_URL = os.environ['DOWNLOAD_URL']


def lambda_handler(event, context):
    text = requests.get(DOWNLOAD_URL, timeout=30).text
    print(text)
