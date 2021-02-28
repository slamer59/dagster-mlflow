import typing
from pathlib import Path

from dagster import (Any, Bool, Enum, EnumValue, Field, Output,
                     OutputDefinition, PresetDefinition,
                     PythonObjectDagsterType, Selector, String,
                     execute_pipeline, pipeline, repository, schedule, solid)
from solids import *

base_path = Path(__file__).parent
# import onnx_utils

# Import mlflow

# https://github.com/dagster-io/dagster/blob/4a91c9d09b50db93e9174c93a4ada0e138e3a046/examples/docs_snippets/docs_snippets/intro_tutorial/basics/e02_solids/multiple_outputs.py
if typing.TYPE_CHECKING:
    DataFrame = list
else:
    DataFrame = PythonObjectDagsterType(list, name="DataFrame")  # type: Any





# To try:
# https://stackoverflow.com/questions/61330816/how-would-you-parameterize-dagster-pipelines-to-run-same-solids-with-multiple-di
# -> https://github.com/dagster-io/dagster/discussions/3047
@pipeline(preset_defs=[
        PresetDefinition.from_files(
            "dev",
            config_files=[
                "/opt/dagster/app/pipeline_run.yaml"
            ],

        )
    ])
def classify_wines():
    load_wines = load_wines_dataset()
    build_features(load_wines)
    tr_test_split = train_test_split(load_wines)

    # ml_model(*tr_test_split)
    models_metrics_result = []
    for k in dict_classifiers.keys():
        model_name = k.replace(" ", "_").lower()
        model = ml_model.alias(model_name)
        output_m = model(*tr_test_split)
        models_metrics_result.append(output_m)

    merge_results(models_metrics_result)



@pipeline
def my_pipeline_mlflow_0():
    use_model()
