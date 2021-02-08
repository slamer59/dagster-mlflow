from minio import Minio
from minio.error import S3Error


def main():
    # Create a client with the MinIO server playground, its access key
    # and secret key.
    client = Minio(
        "0.0.0.0:9000", access_key="mlflow_user", secret_key="mlflow_pwd", secure=False
    )

    # Make 'output' bucket if not exist.
    found = client.bucket_exists("output")
    if not found:
        client.make_bucket("output")
    else:
        print("Bucket 'output' already exists")

    # Upload '/home/user/Photos/asiaphotos.zip' as object name
    # 'asiaphotos-2015.zip' to bucket 'output'.
    client.fput_object(
        "output",
        "test_minio_s3.py",
        "./src/test_minio_s3.py",
    )
    print(
        "/src/test_minio_s3.py is successfully uploaded as "
        "object 'test_minio_s3.py' to bucket 'output'."
    )


if __name__ == "__main__":
    try:
        main()
    except S3Error as exc:
        print("error occurred.", exc)
