import os
import boto3
import string
from datetime import datetime
import random
import pandas as pd
import json
from petpy import Petfinder

api_key = os.getenv('PETFINDER_API_KEY')
secret_key = os.getenv('PETFINDER_SECRET_KEY')
BUCKET_NAME = os.getenv('S3_BUCKET_NAME')

now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
random_string = ''.join(random.choices(string.ascii_lowercase, k=10))
parquet_file_name = f"{now}_{random_string}"

def handler(event, context):
    print("Starting the handler")
    pf = Petfinder(key=api_key, secret=secret_key)
    dogs = pf.animals(animal_type='dog', status='adoptable', location='Boston, MA', distance=20,
                    results_per_page=2, pages=1)["animals"]
    dog_list = []
    for dog in dogs:
        desired_keys = ["id", "url", "name"]
        new_dict = {key: dog[key] for key in desired_keys}
        dog_list.append(new_dict)
    dog_pd = pd.json_normalize(dog_list)
    dog_pd.to_parquet(f"/tmp/{parquet_file_name}.gzip", compression="gzip")

    s3 = boto3.client("s3")
    s3.upload_file(f"/tmp/{parquet_file_name}.gzip", BUCKET_NAME, f"{parquet_file_name}.gzip")

    return {
        'statusCode': 200,
        'body': json.dumps('Data written to S3')
    }