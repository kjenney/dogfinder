import boto3
import pandas as pd
import os
import time
import urllib.parse
import codecs
import json

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

        response = athena.get_query_results(QueryExecutionId=query_execution_id)
        data = response['ResultSet']['Rows']
        results = []
        for row in data[1:]:
            row_dict = {}
            for i, col in enumerate(row['Data']):
                row_dict[data[0]['Data'][i]['VarCharValue']] = col['VarCharValue']
            results.append(row_dict)
        return results

    except Exception as e:
        print(f"An error occurred while running the Athena query: {str(e)}")

def handler(event, context):
    print("Running data handler")
    query_results = run_query(f"select * from {GLUE_TABLE_NAME}")
    return {
        'statusCode': 200,
        'headers': {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": 'GET, POST, PUT, DELETE, OPTIONS'
        },
        'body': query_results
    }