from sklearn import datasets

import pandas as pd
import numpy as np
import time
from dagster import execute_pipeline, pipeline, solid
from dagster import (
    Bool,
    Field,
    Output,
    OutputDefinition,
    PythonObjectDagsterType,
    execute_pipeline,
    pipeline,
    solid,
    String,
    Selector,
    Enum,
    EnumValue,
    Field,
    Any
)
import typing

# https://github.com/dagster-io/dagster/blob/4a91c9d09b50db93e9174c93a4ada0e138e3a046/examples/docs_snippets/docs_snippets/intro_tutorial/basics/e02_solids/multiple_outputs.py
if typing.TYPE_CHECKING:
    DataFrame = list
else:
    DataFrame = PythonObjectDagsterType(list, name="DataFrame")  # type: Any


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

    X_train, Y_train, X_test, Y_test = train_test_split(
        data["data"], data["target"], test_size=0.2
    )
    context.log.info(
        """Samples in:
         - training data: {l_data_train}
         - test data: {l_data_test}""".format(
            l_data_train=len(X_train), l_data_test=len(X_test)
        )
    )
    yield Output(X_train, "X_train")
    yield Output(Y_train, "Y_train")
    yield Output(X_test, "X_test")
    yield Output(Y_test, "Y_test")


from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC, LinearSVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn import tree
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.gaussian_process.kernels import RBF
from sklearn.ensemble import RandomForestClassifier


from sklearn.model_selection import GridSearchCV
from sklearn.metrics import accuracy_score

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
@solid(config_schema=Field(Any))
def ml_model(context, X_train, Y_train, X_test, Y_test):
    key = context.solid_config  # 'Logistic Regression'
    # key = 'Logistic Regression'
    context.log.info("ML Model: {}".format(key))
    t_start = time.process_time()

    count = 0
    classifier = dict_classifiers[key]
    df_results = pd.DataFrame(
        data=np.zeros(shape=(1, 4)),
        columns=["classifier", "train_score", "test_score", "training_time"],
    )
    grid = GridSearchCV(
        classifier["classifier"],
        classifier["params"],
        refit=True,
        cv=10,  # 9+1
        scoring="accuracy",  # scoring metric
        n_jobs=-1,
    )
    estimator = grid.fit(X_train, Y_train)
    t_end = time.process_time()
    t_diff = t_end - t_start
    train_score = estimator.score(X_train, Y_train)
    test_score = estimator.score(X_test, Y_test)
    df_results.loc[count, "classifier"] = key
    df_results.loc[count, "train_score"] = train_score
    df_results.loc[count, "test_score"] = test_score
    df_results.loc[count, "training_time"] = t_diff

    context.log.info("trained {c} in {f:.2f} s".format(c=key, f=t_diff))
    # count+=1
    # plot_learning_curve(estimator,
    #                         "{}".format(key),
    #                         X_train,
    #                         Y_train,
    #                         ylim=(0.75,1.0),
    #                         cv=10)
    return df_results


@pipeline
def classify_wines():
    load_wines = load_wines_dataset()
    build_features(load_wines)
    tr_test_split = train_test_split(load_wines)

    ml_model(*tr_test_split)

    # log_reg = ml_model.alias("Random Forest")
    # nearest_neighbors = ml_model.alias('nearest_neighbors')
    # log_reg(*tr_test_split)
    # nearest_neighbors(*tr_test_split)