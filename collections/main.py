from petpy import Petfinder
import os
import boto3
from dotenv import load_dotenv
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

load_dotenv()

api_key = os.getenv('PETFINDER_API_KEY')
secret_key = os.getenv('PETFINDER_SECRET_KEY')
bucket_name = os.getenv('BUCKET_NAME')
parquet_file_name = os.getenv('PARQUET_FILE_NAME')

pf = Petfinder(key=api_key, secret=secret_key)
dogs = pf.animals(animal_type='dog', status='adoptable', location='Boston, MA', distance=20,
                  results_per_page=2, pages=1)["animals"] #, return_df=True)
dog_list = []
for dog in dogs:
    desired_keys = ["id", "url", "name"]
    new_dict = {key: dog[key] for key in desired_keys}
    dog_list.append(new_dict)
dog_pd = pd.json_normalize(dog_list)
dog_table = pa.Table.from_pandas(dog_pd)
pq.write_table(dog_table, f"/tmp/{parquet_file_name}")

s3 = boto3.client("s3")
s3.upload_file(f"/tmp/{parquet_file_name}", bucket_name, parquet_file_name)


