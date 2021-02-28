

from pprint import pprint
from dagster.core.definitions.decorators.sensor import sensor
from  mlflow.tracking import MlflowClient

# Exemple from https://docs.dagster.io/overview/schedules-sensors/sensors
# and https://www.mlflow.org/docs/latest/model-registry.html#listing-and-searching-mlflow-models
# With mlflow model registered instead of new file
@sensor(pipeline_name="my_pipeline_mlflow_0")
def my_directory_sensor(_context):
    experiment_name = "Classify Wine"
    tracking_uri = "http://mlflow:5000"
    client = MlflowClient(tracking_uri=tracking_uri)
    for rm in client.list_registered_models():
        pprint(dict(rm), indent=4)

    
    # for filename in os.listdir(MY_DIRECTORY):
    #     filepath = os.path.join(MY_DIRECTORY, filename)
    #     if os.path.isfile(filepath):
    #         yield RunRequest(
    #             run_key=filename,
    #             run_config={"solids": {"process_file": {"config": {"filename": filename}}}},
    #         )