#!/bin/bash

environment=$1

path=/tmp

if [ "${environment}" = "dev" ]; then

gcloud auth activate-service-account <service_account>  --key-file=/secrets/db-backup-account.json --project=<project_name>
gcloud config set project <project_name>
gcloud container clusters get-credentials kubernetes-prebid-cloudops --zone us-east1-c --project <project_name>

# echo "Delete the prebid-ops-file-date-list secret"

kubectl --namespace=prebid delete secret prebid-ops-file-date-list

echo "Update prebid-ops-file-date-list"

kubectl --namespace=prebid create secret generic prebid-ops-file-date-list \
    --from-file=barron_lmd=${path}/barron_lmd \
    --from-file=nypost_lmd=${path}/nypost_lmd \
    --from-file=marketwatch_lmd=${path}/marketwatch_lmd

gcloud container clusters get-credentials kubernetes-prebid-cloudops --zone europe-north1-a --project <project_name>

# echo "Delete the prebid-ops-file-date-list secret"

kubectl --namespace=prebid delete secret prebid-ops-file-date-list

echo "Update prebid-ops-file-date-list"

kubectl --namespace=prebid create secret generic prebid-ops-file-date-list \
    --from-file=barron_lmd=${path}/barron_lmd \
    --from-file=nypost_lmd=${path}/nypost_lmd \
    --from-file=marketwatch_lmd=${path}/marketwatch_lmd

fi

if [ "${environment}" = "prod" ]; then

gcloud auth activate-service-account <service_account>  --key-file=/secrets/db-backup-account.json --project=<project_name>
gcloud config set project <project_name>
gcloud container clusters get-credentials kubernetes-prebid-cloudops --zone us-east1-c --project <project_name>

kubectl --namespace=prebid delete secret prebid-ops-file-date-list

echo "Update prebid-ops-file-date-list"

kubectl --namespace=prebid create secret generic prebid-ops-file-date-list \
    --from-file=barron_lmd=${path}/barron_lmd \
    --from-file=nypost_lmd=${path}/nypost_lmd \
    --from-file=marketwatch_lmd=/tmp${path}/marketwatch_lmd

gcloud container clusters get-credentials kubernetes-prebid-cloudops --zone europe-north1-a --project <project_name>

kubectl --namespace=prebid delete secret prebid-ops-file-date-list

kubectl --namespace=prebid create secret generic prebid-ops-file-date-list \
    --from-file=barron_lmd=${path}/barron_lmd \
    --from-file=nypost_lmd=${path}/tmp/nypost_lmd \
    --from-file=marketwatch_lmd=${path}/marketwatch_lmd

fi
