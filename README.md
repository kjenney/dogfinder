# dogfinder

A static website hosted on S3 with data collection using Lambda. This architecture that is extremely cost-efficient. It's using the Petfinder API to save information on specific dogs that are ready to be adopted.

## Components

### Collections 

An AWS Lambda that collects information about dogs in my area from the Petfinder API. Saves the data in Parquet formet in S3.

### Data API

An AWS API Gateway paired with an AWS Lambda that uses AWS Athana to query the data collected in S3.

### User Management

An AWS Cognito pool configured to be used by the website.

## Website

Static files including Javascript hosted on an S3 bucket.


