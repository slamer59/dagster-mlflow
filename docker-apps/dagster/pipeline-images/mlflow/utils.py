import typing
from pathlib import Path

from dagster import (Any, Bool, Enum, EnumValue, Field, Output,
                     OutputDefinition, PresetDefinition,
                     PythonObjectDagsterType, Selector, String,
                     execute_pipeline, pipeline, solid)

base_path = Path(__file__).parent
# import onnx_utils

# Import mlflow
import mlflow
import mlflow.sklearn

# https://github.com/dagster-io/dagster/blob/4a91c9d09b50db93e9174c93a4ada0e138e3a046/examples/docs_snippets/docs_snippets/intro_tutorial/basics/e02_solids/multiple_outputs.py
if typing.TYPE_CHECKING:
    DataFrame = list
else:
    DataFrame = PythonObjectDagsterType(list, name="DataFrame")  # type: Any







def yield_artifacts(run_id, path=None):
    """Yield all artifacts in the specified run"""
    client = mlflow.tracking.MlflowClient()
    for item in client.list_artifacts(run_id, path):
        if item.is_dir:
            yield from yield_artifacts(run_id, item.path)
        else:
            yield item.path


def fetch_logged_data(run_id):
    """Fetch params, metrics, tags, and artifacts in the specified run"""
    client = mlflow.tracking.MlflowClient()
    data = client.get_run(run_id).data
    # Exclude system tags: https://www.mlflow.org/docs/latest/tracking.html#system-tags
    tags = {k: v for k, v in data.tags.items() if not k.startswith("mlflow.")}
    artifacts = list(yield_artifacts(run_id))
    return {
        "params": data.params,
        "metrics": data.metrics,
        "tags": tags,
        "artifacts": artifacts,
    }
