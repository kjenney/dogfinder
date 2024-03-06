# collections

Collects data from PetFinder API. Saves to S3 bucket in Parquet format.

## Layers

Uses Lambda Layers. Pandas is managed and petpy is built here:

```
pip install -r petpy -t ./petpy
```

To deploy use `sls deploy`.
