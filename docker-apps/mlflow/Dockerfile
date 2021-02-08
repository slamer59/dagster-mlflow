FROM continuumio/miniconda3

# Install the package as normal:
ADD environment.yml .
RUN conda env create -f environment.yml

WORKDIR /mlflow/

ENV BACKEND_FILE=/mlflow/data/mlflow.sqlite 
ENV BACKEND_URI=/mlflow/store
ENV PORT_LISTEN=5000

ENV ARTIFACT_ROOT=/mlflow/mlflow-artifacts

RUN mkdir -p /mlflow/data
RUN touch ${BACKEND_FILE}

# activate the mlflow environment
ENV PATH /opt/conda/envs/mlflow/bin:$PATH

EXPOSE ${PORT_LISTEN}

CMD echo "Artifact Root is ${ARTIFACT_ROOT}" && \
  mlflow server \
  --backend-store-uri ${BACKEND_URI} \
  --default-artifact-root ${ARTIFACT_ROOT} \
  --host 0.0.0.0 \
  --port ${PORT_LISTEN}
