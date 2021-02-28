# dagster-mlflow-exemple

## Multiple scikit learn model are laucnhed and tracked into mlflow instance

A short test for mlflow integration to dagster

I follow this [simple tutorial](https://jonathonbechtel.com/blog/2018/02/06/wines/ ) from [Jonathon Bechtel](http://github.com/jbechtel) 
which test multiple models in a loop. I wanted to implement it with dagster and maybe at the end to play it together with mlflow.

![First Pipeline](./docs/First%20pipeline%20dagster.png)

Configuration of solids:

```yaml
solids:
  decision_tree:
    config: "Decision Tree"
  gradient_boosting_classifier:
    config: "Gradient Boosting Classifier"
  linear_svm:
    config: "Linear SVM"
  logistic_regression:
    config: "Logistic Regression"
  naive_bayes:
    config: "Naive Bayes"
  nearest_neighbors:
    config: "Nearest Neighbors"
  random_forest:
    config: "Random Forest"
```

## Sensor launch a solid when mlflow register a new model

![First Sensors with mlflow](./docs/sensor%20with%20mlflow.gif)

Todo list:

- [x] Add mlflow to log models
- [ ] Attached a VOLUME to dagster Docker image to refresh repo.py / config.yaml more dynamically.
- [ ] See if it is possible to integrate solid configuration dynamically, e.g. another solid can get the list of parameters from a file then pass it to dynamically launch multiple solids (models)
- [ ] Launch solids in parallel
- [ ] Trigger dagster when a new parameter is registered.
- [x] Construct solid dynamically from an mlflow [model signature](https://www.mlflow.org/docs/latest/_modules/mlflow/models/signature.html). Ex? [With papermill](https://www.youtube.com/watch?v=9WKtBFg2bUo).
- [ ] Test [sensors event based triggering](https://docs.dagster.io/overview/schedules-sensors/sensors)


Project Organization
------------

    ├── LICENSE
    ├── Makefile           <- Makefile with commands like `make data` or `make train`
    ├── README.md          <- The top-level README for developers using this project.
    ├── data
    │   ├── external       <- Data from third party sources.
    │   ├── interim        <- Intermediate data that has been transformed.
    │   ├── processed      <- The final, canonical data sets for modeling.
    │   └── raw            <- The original, immutable data dump.
    │
    ├── docs               <- A default Sphinx project; see sphinx-doc.org for details
    │
    ├── models             <- Trained and serialized models, model predictions, or model summaries
    │
    ├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
    │                         the creator's initials, and a short `-` delimited description, e.g.
    │                         `1.0-jqp-initial-data-exploration`.
    │
    ├── references         <- Data dictionaries, manuals, and all other explanatory materials.
    │
    ├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
    │   └── figures        <- Generated graphics and figures to be used in reporting
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt`
    │
    ├── setup.py           <- makes project pip installable (pip install -e .) so src can be imported
    ├── src                <- Source code for use in this project.
    │   ├── __init__.py    <- Makes src a Python module
    │   │
    │   ├── data           <- Scripts to download or generate data
    │   │   └── make_dataset.py
    │   │
    │   ├── features       <- Scripts to turn raw data into features for modeling
    │   │   └── build_features.py
    │   │
    │   ├── models         <- Scripts to train models and then use trained models to make
    │   │   │                 predictions
    │   │   ├── predict_model.py
    │   │   └── train_model.py
    │   │
    │   └── visualization  <- Scripts to create exploratory and results oriented visualizations
    │       └── visualize.py
    │
    └── tox.ini            <- tox file with settings for running tox; see tox.readthedocs.io


--------

<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>
