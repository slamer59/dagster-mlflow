import boto3

AWS_ACCESS_KEY_ID="mlflow_user"
AWS_SECRET_ACCESS_KEY= "mlflow_pwd"
S3_LOCATION = "http://0.0.0.0:9000"
s3 = boto3.resource(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    endpoint_url=S3_LOCATION
)
