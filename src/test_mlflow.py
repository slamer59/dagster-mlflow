from mlflow.tracking import MlflowClient
import mlflow

import os

tracking_uri = "http://127.0.0.1:5000"

os.environ["AWS_ACCESS_KEY_ID"] = "mlflow_user"
os.environ["AWS_SECRET_ACCESS_KEY"] = "mlflow_pwd"
os.environ["MLFLOW_S3_ENDPOINT_URL"] = "http://127.0.0.1:9000"

artifact_location = "s3://mlflow-bucket"

mlflow.set_tracking_uri(tracking_uri)

# client = MlflowClient(tracking_uri=tracking_uri)
# experiments = mlflow.list_experiments()
# experiment_names = [experiment.name for experiment in experiments]
# print(experiment_names)

experiment_name = "Classify Wine"
experiment = mlflow.get_experiment_by_name(experiment_name)

if experiment is None:
    print('create')
    experiment = mlflow.create_experiment(
        experiment_name, artifact_location=artifact_location
    )
else:
    experiment = mlflow.get_experiment_by_name(experiment_name)

print(experiment)
