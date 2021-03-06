from dagster import pipeline, repository, schedule, solid


@solid
def hello(_):
    return 1


@pipeline
def my_pipeline_mlflow():
    hello()


@schedule(cron_schedule="* * * * *", pipeline_name="my_pipeline_mlflow", execution_timezone="US/Central")
def my_schedule(_context):
    return {}


@repository
def deploy_docker_repository():
    return [my_pipeline_mlflow, my_schedule]
