#!/bin/bash

mlflow server \
    --host "$MLFLOW_SERVER_HOST" \
    --port "$MLFLOW_SERVER_PORT" \
    --workers "$MLFLOW_SERVER_WORKERS"