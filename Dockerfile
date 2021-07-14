FROM python:3.7-slim-buster

RUN ln -s /usr/bin/python3 /usr/bin/python

RUN set -ex \
    && apt-get update -y \
    && apt-get install -y wget bash curl gcc openssl

RUN apt-get update -y && apt-get install -y postgresql postgresql-client postgresql-contrib libpq-dev


RUN python -m pip install --upgrade pip \
    pip install psycopg2 google-cloud-storage gcloud gsutil openpyxl

# Install gsutil
RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
RUN apt-get install -y apt-transport-https ca-certificates gnupg gnupg2 gnupg1
RUN curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -
RUN apt-get update -y && apt-get install -y google-cloud-sdk

# Install kubectl
RUN curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
RUN curl -LO "https://dl.k8s.io/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl.sha256"
RUN install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
RUN mkdir -p ~/.local/bin/kubectl
RUN mv ./kubectl ~/.local/bin/kubectl
RUN kubectl version --client


RUN mkdir /db_config_scripts
RUN mkdir -p /secrets/
RUN touch /tmp/barron_lmd
RUN touch /tmp/nypost_lmd
RUN touch /tmp/marketwatch_lmd

COPY set_k8_secres.sh /db_config_scripts/set_k8_secres.sh
RUN chmod +x /db_config_scripts/set_k8_secres.sh
COPY download_gcs_blob.py /db_config_scripts/
COPY update_prebid_server_tables.py /db_config_scripts/

WORKDIR /db_config_scripts