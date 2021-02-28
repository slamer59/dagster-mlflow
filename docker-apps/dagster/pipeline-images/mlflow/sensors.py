import typing
from pathlib import Path

from dagster import (Any, Bool, Enum, EnumValue, Field, Output,
                     OutputDefinition, PresetDefinition,
                     PythonObjectDagsterType, Selector, String,
                     execute_pipeline, pipeline, repository, schedule, solid)
from dagster.core.definitions.decorators.sensor import sensor
base_path = Path(__file__).parent
from mlflow.tracking import MlflowClient

# https://github.com/dagster-io/dagster/blob/4a91c9d09b50db93e9174c93a4ada0e138e3a046/examples/docs_snippets/docs_snippets/intro_tutorial/basics/e02_solids/multiple_outputs.py
if typing.TYPE_CHECKING:
    DataFrame = list
else:
    DataFrame = PythonObjectDagsterType(list, name="DataFrame")  # type: Any

# Exemple from https://docs.dagster.io/overview/schedules-sensors/sensors
# and https://www.mlflow.org/docs/latest/model-registry.html#listing-and-searching-mlflow-models
# With mlflow model registered instead of new file
@sensor(pipeline_name="my_pipeline_mlflow_0")
def my_directory_sensor(_context):
    experiment_name = "Classify Wine"
    tracking_uri = "http://mlflow:5000"
    client = MlflowClient(tracking_uri=tracking_uri)
    for rm in client.list_registered_models():
        context.log.info("Registered model: " + dict(rm))
        run_id = dict(dict(rm)['latest_versions'][0])['run_id']

        yield RunRequest(
                run_key=run_id,
                run_config={"solids": {"use_model": {"config": {"run_id": run_id}}}},
            )

