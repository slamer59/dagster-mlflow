import time
import typing
from pathlib import Path

import mlflow
import mlflow.sklearn
import numpy
import numpy as np
import pandas as pd
from dagster import (Any, Bool, Enum, EnumValue, Field, Output,
                     OutputDefinition, PresetDefinition,
                     PythonObjectDagsterType, Selector, String,
                     execute_pipeline, pipeline, repository, schedule, solid)
from sklearn import datasets

# https://github.com/dagster-io/dagster/blob/4a91c9d09b50db93e9174c93a4ada0e138e3a046/examples/docs_snippets/docs_snippets/intro_tutorial/basics/e02_solids/multiple_outputs.py
if typing.TYPE_CHECKING:
    DataFrame = list
else:
    DataFrame = PythonObjectDagsterType(list, name="DataFrame")  # type: Any
from sklearn import tree
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from utils import *

base_path = Path(__file__).parent
# https://jonathonbechtel.com/blog/2018/02/06/wines/

# Step 1
@solid
def load_wines_dataset(context):
    wines = datasets.load_wine()
    return wines


@solid
def build_features(context, wines):
    features = pd.DataFrame(data=wines["data"], columns=wines["feature_names"])
    data = features
    # context.log.info(data.head())
    data["target"] = wines["target"]
    data["class"] = data["target"].map(lambda ind: wines["target_names"][ind])
    return data


@solid(
    output_defs=[
        OutputDefinition(name="X_train"),
        OutputDefinition(name="Y_train"),
        OutputDefinition(name="X_test"),
        OutputDefinition(name="Y_test"),
    ]
)
def train_test_split(context, data):
    from sklearn.model_selection import train_test_split

    X_train, X_test, Y_train, Y_test = train_test_split(
        data["data"], data["target"], test_size=0.2
    )
    context.log.info(
        """Samples in:
         - training data X: {l_data_train_x}
         - test data X: {l_data_test_x}
         - training data Y: {l_data_train_y}
         - test data Y: {l_data_test_y}
         """.format(
            l_data_train_x=len(X_train),
            l_data_test_x=len(X_test),
            l_data_train_y=len(Y_train),
            l_data_test_y=len(Y_test),
        )
    )
    yield Output(X_train, "X_train")
    yield Output(Y_train, "Y_train")
    yield Output(X_test, "X_test")
    yield Output(Y_test, "Y_test")


dict_classifiers = {
    "Logistic Regression": {
        "classifier": LogisticRegression(),
        "params": [
            {"penalty": ["l1", "l2"], "C": [0.001, 0.01, 0.1, 1, 10, 100, 1000]}
        ],
    },
    "Nearest Neighbors": {
        "classifier": KNeighborsClassifier(),
        "params": [{"n_neighbors": [1, 3, 5, 10], "leaf_size": [3, 30]}],
    },
    "Linear SVM": {
        "classifier": SVC(),
        "params": [
            {"C": [1, 10, 100, 1000], "gamma": [0.001, 0.0001], "kernel": ["linear"]}
        ],
    },
    "Gradient Boosting Classifier": {
        "classifier": GradientBoostingClassifier(),
        "params": [
            {
                "learning_rate": [0.05, 0.1],
                "n_estimators": [50, 100, 200],
                "max_depth": [3, None],
            }
        ],
    },
    "Decision Tree": {
        "classifier": tree.DecisionTreeClassifier(),
        "params": [{"max_depth": [3, None]}],
    },
    "Random Forest": {"classifier": RandomForestClassifier(), "params": {}},
    "Naive Bayes": {"classifier": GaussianNB(), "params": {}},
}

# https://docs.dagster.io/tutorial/advanced_solids
@solid(config_schema=String)  # {"classifier_name": str})
def ml_model(context, X_train, Y_train, X_test, Y_test):
    key = context.solid_config  # ["classifier_name"]  # 'Logistic Regression'
    # key = 'Logistic Regression'
    context.log.info("ML Model: {}".format(key))
    context.log.info(
        """Samples in:
        - training data X: {l_data_train_x}
        - test data X: {l_data_test_x}
        - training data Y: {l_data_train_y}
        - test data Y: {l_data_test_y}
        """.format(
            l_data_train_x=len(X_train),
            l_data_test_x=len(X_test),
            l_data_train_y=len(Y_train),
            l_data_test_y=len(Y_test),
        )
    )
    t_start = time.process_time()

    count = 0
    classifier = dict_classifiers[key]
    df_results = pd.DataFrame(
        data=np.zeros(shape=(1, 4)),
        columns=["classifier", "train_score", "test_score", "training_time"],
    )
    model_name = classifier["classifier"]

    # enable autologging
    mlflow.sklearn.autolog(log_model_signatures=True, log_models=True)
    experiment_name = "Classify Wine"
    tracking_uri = "http://mlflow:5000"

    # sftp_uri = "sftp://mlflow_user:mlflow_pwd@127.0.0.1:2222/mlflow/mlflow-artifacts"
    # artifact_location=sftp_uri
    import os

    os.environ["AWS_ACCESS_KEY_ID"] = "mlflow_user"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "mlflow_pwd"
    os.environ["MLFLOW_S3_ENDPOINT_URL"] = "http://artifact-store:9000"

    artifact_location = "s3://mlflow-bucket"
    mlflow.set_tracking_uri(tracking_uri)
    context.log.info("Mlfow tracking URI %s " % tracking_uri)

    experiment = mlflow.get_experiment_by_name(experiment_name)

    if experiment is None:
        context.log.info("Create Experiment: %s" % experiment_name)
        experiment_id = mlflow.create_experiment(
            experiment_name, artifact_location=artifact_location
        )
        experiment = mlflow.get_experiment(experiment_id)
    else:
        context.log.info("Experiment exist: %s" % experiment_name)
        experiment = mlflow.get_experiment_by_name(experiment_name)

    context.log.info("Expermient name: %s" % experiment)
    context.log.info("Experiment_id: {}".format(experiment.experiment_id))
    context.log.info("Artifact Location: {}".format(experiment.artifact_location))

    with mlflow.start_run(experiment_id=experiment.experiment_id) as run:
        context.log.info("Mlflow Start run %s" % run.info)

        grid = GridSearchCV(
            model_name,
            classifier["params"],
            refit=True,
            cv=10,  # 9+1
            scoring="accuracy",  # scoring metric
            n_jobs=-1,
        )
        estimator = grid.fit(X_train, Y_train)

        params, metrics, tags, artifacts = fetch_logged_data(run.info.run_id)
        mlflow.sklearn.log_model(
            estimator, "models/sk_model_" + key.replace(" ", "_").lower()
        )

    t_end = time.process_time()
    t_diff = t_end - t_start
    train_score = estimator.score(X_train, Y_train)
    test_score = estimator.score(X_test, Y_test)
    df_results.loc[count, "classifier"] = key
    df_results.loc[count, "train_score"] = train_score
    df_results.loc[count, "test_score"] = test_score
    df_results.loc[count, "training_time"] = t_diff

    context.log.info("trained {c} in {f:.2f} s".format(c=key, f=t_diff))

    return df_results


def log_run(
    gridsearch: GridSearchCV,
    experiment_name: str,
    model_name: str,
    run_index: int,
    conda_env,
    tags={},
):
    """Logging of cross validation results to mlflow tracking server

    Args:
        experiment_name (str): experiment name
        model_name (str): Name of the model
        run_index (int): Index of the run (in Gridsearch)
        conda_env (str): A dictionary that describes the conda environment (MLFlow Format)
        tags (dict): Dictionary of extra data and tags (usually features)
    """

    cv_results = gridsearch.cv_results_
    with mlflow.start_run(run_name=str(run_index)) as run:

        mlflow.log_param("folds", gridsearch.cv)
        print("Logging parameters")

        l_params = gridsearch.param_grid
        for params in l_params:
            for param in params:
                mlflow.log_param(param, cv_results["param_%s" % param][run_index])

        print("Logging metrics")
        for score_name in [score for score in cv_results if "mean_test" in score]:
            mlflow.log_metric(score_name, cv_results[score_name][run_index])
            mlflow.log_metric(
                score_name.replace("mean", "std"),
                cv_results[score_name.replace("mean", "std")][run_index],
            )

        print("Logging model")
        mlflow.sklearn.log_model(
            gridsearch.best_estimator_, model_name, conda_env=conda_env
        )

        print("Logging CV results matrix")
        tempdir = tempfile.TemporaryDirectory().name
        os.mkdir(tempdir)
        timestamp = datetime.now().isoformat().split(".")[0].replace(":", ".")
        filename = "%s-%s-cv_results.csv" % (model_name, timestamp)
        csv = os.path.join(tempdir, filename)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            pd.DataFrame(cv_results).to_csv(csv, index=False)

        mlflow.log_artifact(csv, "cv_results")

        print("Logging extra data related to the experiment")
        mlflow.set_tags(tags)

        run_id = run.info.run_uuid
        experiment_id = run.info.experiment_id
        mlflow.end_run()
        print(mlflow.get_artifact_uri())
        print("runID: %s" % run_id)


@solid
def merge_results(context, models_metrics_result):
    return pd.concat(models_metrics_result)


@solid(config_schema={"run_id": str})
def use_model(context):
    run_id = context.solid_config["run_id"]
    context.log.info("Using mlflow: " + run_id)
