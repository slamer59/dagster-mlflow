from mlflow.tracking import MlflowClient
import mlflow

tracking_uri = "http://127.0.0.1:5000"

client = MlflowClient()
mlflow.set_tracking_uri(tracking_uri)
experiments = client.list_experiments()


print([experiments[0].name])