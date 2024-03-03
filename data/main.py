import boto3
import pandas as pd

# Define the necessary constants
BUCKET_NAME = "your-bucket-name"  # Replace with your actual S3 bucket name
S3_PATH = "your/s3/path/to/parquet/file.parquet"  # Replace with your actual path to the
Parquet file in S3
QUERY = "SELECT * FROM your_table_name"  # Replace with your desired Athena query
ROLE_ARN = "arn:aws:iam::your-account-id:role/your-role-name"  # Replace with your actual IAM
role ARN
REGION_NAME = "us-east-1"  # Adjust this as necessary to match the region of your S3 bucket
and Athena service endpoint

# Create an AWS Session with appropriate credentials
session = boto3.Session(
    aws_access_key_id='your-access-key-id',
    aws_secret_access_key='your-secret-access-key',
    region_name=REGION_NAME
)

# Create an Athena client using the AWS Session
athena = session.client('athena')

def run_query(query):
    try:
        query_execution_id = athena.start_query_execution(
            QueryString=query,
            QueryExecutionContext={
                'Database': BUCKET_NAME
            },
            ResultConfiguration={
                'OutputLocation': f's3://{BUCKET_NAME}/athena-results/'
            },
            WorkGroup='default',
            SessionToken="optional-session-token"  # Omit this if you don't have a session
token
        )['QueryExecutionId']

        response = athena.get_query_execution(QueryExecutionId=query_execution_id)
        while True:
            status = response['QueryExecution']['Status']['State']

            if status == 'SUCCEEDED':
                break

            elif status == 'RUNNING' or status == 'QUEUED':
                # Wait for the query to finish executing
                time.sleep(60)
                response = athena.get_query_execution(QueryExecutionId=query_execution_id)

            elif status == 'FAILED':
                print("Query execution failed:")
                return None

        results_file = response['QueryExecution']['ResultSummary']['Location'] + '/' +
response['QueryExecution']['ResultSummary']['S3Object']
        df = pd.read_csv(results_file, header=0)

        # Display the data for debugging purposes
        print("Data retrieved from the query:")
        print(df.head())

    except Exception as e:
        print(f"An error occurred while running the Athena query: {str(e)}")

# Run the query
run_query(QUERY)
