import yaml
from pathlib import Path
from dagster import (Any, Bool, Enum, EnumValue, Field, Output,
                     OutputDefinition, PresetDefinition,
                     PythonObjectDagsterType, Selector, String,
                     execute_pipeline, pipeline, repository, schedule, solid)


# https://crontab.guru/every-5-minutes
# https://docs.dagster.io/0.8.3/docs/tutorial/advanced_scheduling
@schedule(
    cron_schedule="* * * * *",
    pipeline_name="classify_wines",
    execution_timezone="US/Central",
)
def my_schedule(_context):
    p = Path("/opt/dagster/app/pipeline_run.yaml")
    return yaml.load(open(p))