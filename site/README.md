# site

An S3 bucket for Website Hosting

## Deploy

```
aws cloudformation create-stack --stack-name site-dev --template-body file://s3_website.yml
aws s3 cp index.html s3://{YOUR_BUCKET}
```

## TODO 

* Make the output pretty