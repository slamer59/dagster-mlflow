
from dagster import (Any, Bool, Enum, EnumValue, Field, Output,
                     OutputDefinition, PresetDefinition,
                     PythonObjectDagsterType, Selector, String,
                     execute_pipeline, pipeline, repository, schedule, solid)
                     
# https://crontab.guru/every-5-minutes
@schedule(cron_schedule="*/5 * * * *", pipeline_name="classify_wines", execution_timezone="US/Central")
def my_schedule(_context):
    return {}