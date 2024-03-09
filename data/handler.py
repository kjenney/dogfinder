import boto3
import pandas as pd
import os
import time

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
                'Database': GLUE_DATABASE_NAME,
                'Catalog': 'AwsDataCatalog'
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

        results_file = response['QueryExecution']['ResultSummary']['Location'] + '/' + response['QueryExecution']['ResultSummary']['S3Object']
        df = pd.read_csv(results_file, header=0)

        # Display the data for debugging purposes
        print("Data retrieved from the query:")
        print(df.head())

    except Exception as e:
        print(f"An error occurred while running the Athena query: {str(e)}")

def handler(event, context):
    print("Running data handler")
    # Run the query
    run_query(f"SELECT * FROM \"AwsDataCatalog\".\"{GLUE_DATABASE_NAME}\".\"{GLUE_TABLE_NAME}\" limit 10;")