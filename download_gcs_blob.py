import os,sys
from google.cloud import storage
from google.oauth2.service_account import Credentials
import datetime
import subprocess
import update_prebid_server_tables

bucket_name = os.getenv('PREBID_CONFIG_AUCTION_BUCKET_NAME', '')
project_name = os.getenv('GCP_PROJECT', '')
pbs_position_map_lmd = os.getenv('PBS_POSITION_MAP_LAST_MODIFIED_DATE', '')
pbs_barrons_lmd = os.getenv('PBS_BARRONS_LAST_MODIFIED_DATE', '2021-06-01 17:06:52')
print("latest_date: {}".format(pbs_barrons_lmd))
pbs_marketwatch_lmd = os.getenv('PBS_MARKET_WATCH_LAST_MODIFIED_DATE', '2021-06-01 17:06:52')
print("latest_date: {}".format(pbs_marketwatch_lmd))
print(pbs_marketwatch_lmd)
pbs_nypost_lmd = os.getenv('PBS_NY_POST_LAST_MODIFIED_DATE', '2021-06-01 17:06:52')
print("latest_date: {}".format(pbs_nypost_lmd))
print(pbs_nypost_lmd)

file_list = []

count = 0

def get_gcp_project():

    return os.getenv('GCP_PROJECT', '')


def get_gcs_client():

    gcp_key_path = os.getenv(
        'GOOGLE_APPLICATION_CREDENTIALS',
        '/secrets/db-backup-account.json'
    )
    auth = Credentials.from_service_account_file(gcp_key_path)
    return storage.Client(project=get_gcp_project(), credentials=auth)


def list_blobs(bucket_name,count):

    if pbs_barrons_lmd is None:
        exit()
    if pbs_marketwatch_lmd is None:
        exit()
    if pbs_nypost_lmd is None:
        exit()
    gcs_client = get_gcs_client()
    blobs = gcs_client.list_blobs(bucket_name)
    for blob in blobs:
        source_blob_name = blob.name
        count += 1
        blob_exist_date = blob.updated.strftime("%Y-%m-%d %H:%M:%S")
        destination_file_name = '/tmp/{}'.format(source_blob_name)
        path = "/tmp"
        environment = "dev"
        converted_lmd_barrons = datetime.datetime.fromisoformat(pbs_barrons_lmd).timestamp()
        converted_lmd_marketwatch = datetime.datetime.fromisoformat(pbs_marketwatch_lmd).timestamp()
        converted_lmd_nypost = datetime.datetime.fromisoformat(pbs_nypost_lmd).timestamp()
        exist_date = datetime.datetime.fromisoformat(blob_exist_date).timestamp()
        blob_lower_case_name = source_blob_name.lower()
        if "barron's" in blob_lower_case_name:
            if float(exist_date) > float(converted_lmd_barrons):
                file_list.append(source_blob_name)
                download_blob(bucket_name, source_blob_name, destination_file_name)
                print("Downloaded: {}".format(destination_file_name))
                print("Updated: {}".format(blob.updated))
                f = open("/tmp/barron_lmd", "w")
                f.write(blob_exist_date)
                f.close()
                # script = "bash /db_config_scripts/set_k8_secres.sh {}".format(environment)
                # print(script)
                # subprocess.Popen(script, shell=True).wait()
            else:
                print("Files are not updated")
        if "marketwatch" in blob_lower_case_name:
            if float(exist_date) > float(converted_lmd_marketwatch):
                file_list.append(source_blob_name)
                download_blob(bucket_name, source_blob_name, destination_file_name)
                print("Downloaded: {}".format(destination_file_name))
                print("Updated: {}".format(blob.updated))
                f = open("/tmp/marketwatch_lmd", "w")
                f.write(blob_exist_date)
                f.close()
                # script = "sh /db_config_scripts/set_k8_secres.sh {}".format(environment)
                # print(script)
                # subprocess.Popen(script, shell=True).wait()
            else:
                print("Files are not updated")
        if "nypost" in blob_lower_case_name:
            if float(exist_date) > float(converted_lmd_nypost):
                file_list.append(source_blob_name)
                download_blob(bucket_name, source_blob_name, destination_file_name)
                print("Downloaded: {}".format(destination_file_name))
                print("Updated: {}".format(blob.updated))
                f = open("/tmp/nypost_lmd", "w")
                f.write(blob_exist_date)
                f.close()
                # script = "sh /db_config_scripts/set_k8_secres.sh {}".format(environment)
                # print(script)
                # subprocess.Popen(script, shell=True).wait()
            else:
                print("Files are not updated")
    script = "bash /db_config_scripts/set_k8_secres.sh {}".format(environment)
    print(script)
    subprocess.Popen(script, shell=True).wait()
    print("Trigger the script")
    print(file_list)
    update_prebid_server_tables.main(file_list)
    return file_list


def download_blob(bucket_name, source_blob_name, destination_file_name):

    gcs_client = get_gcs_client()
    bucket = gcs_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)


if __name__ == '__main__':
    list_blobs(bucket_name,count)
