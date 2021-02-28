import typing
from pathlib import Path

from dagster import (Any, Bool, Enum, EnumValue, Field, Output,
                     OutputDefinition, PresetDefinition,
                     PythonObjectDagsterType, Selector, String,
                     execute_pipeline, pipeline, repository, schedule, solid)

base_path = Path(__file__).parent

# https://github.com/dagster-io/dagster/blob/4a91c9d09b50db93e9174c93a4ada0e138e3a046/examples/docs_snippets/docs_snippets/intro_tutorial/basics/e02_solids/multiple_outputs.py
if typing.TYPE_CHECKING:
    DataFrame = list
else:
    DataFrame = PythonObjectDagsterType(list, name="DataFrame")  # type: Any

from pipelines import *
from schedulers import *
from sensors import *

@repository
def deploy_docker_repository():
    return [my_pipeline_mlflow_0, classify_wines, my_schedule, my_directory_sensor]

