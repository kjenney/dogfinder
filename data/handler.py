import boto3
import pandas as pd
import os
import time
import urllib.parse
import codecs

GLUE_DATABASE_NAME = os.getenv('GLUE_DATABASE_NAME')
RESULTS_BUCKET_NAME = os.getenv('RESULTS_BUCKET_NAME')
ATHENA_WORKGROUP_NAME = os.getenv('ATHENA_WORKGROUP_NAME')
GLUE_TABLE_NAME = os.getenv('GLUE_TABLE_NAME')

athena = boto3.client('athena')

def run_query(query):
    try:
        query_execution_id = athena.start_query_execution(
            QueryString=query,
            QueryExecutionContext={
                'Database': GLUE_DATABASE_NAME
            },
            ResultConfiguration={
                'OutputLocation': f's3://{RESULTS_BUCKET_NAME}/athena-results/'
            },
            WorkGroup=ATHENA_WORKGROUP_NAME,
        )['QueryExecutionId']

        response = athena.get_query_execution(QueryExecutionId=query_execution_id)
        print(f"Query {query_execution_id} running")
        while True:
            status = response['QueryExecution']['Status']['State']
            if status == 'SUCCEEDED':
                break
            elif status == 'RUNNING' or status == 'QUEUED':
                time.sleep(5)
                response = athena.get_query_execution(QueryExecutionId=query_execution_id)
            elif status == 'FAILED':
                reason = response['QueryExecution']['Status']['StateChangeReason']
                print(f"Query execution failed with: {reason}")
                return None
                break

        results_file = response['QueryExecution']['ResultConfiguration']['OutputLocation']
        parsed_url = urllib.parse.urlparse(results_file)
        bucket_name = parsed_url.netloc.split("/")[0]
        filename = parsed_url.path.split("/")[-1]
        
        s3 = boto3.resource("s3")
        s3_object = s3.Object(bucket_name, filename)
        line_stream = codecs.getreader("utf-8")

        print("Output from the query is:")
        for line in line_stream(s3_object.get()['Body']):
            print(line)

    except Exception as e:
        print(f"An error occurred while running the Athena query: {str(e)}")

def handler(event, context):
    print("Running data handler")
    run_query(f"select * from {GLUE_TABLE_NAME}")