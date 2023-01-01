# import the libraries
from datetime import timedelta
# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG
# Operators; we need this to write tasks!
from airflow.operators.bash_operator import BashOperator
# This makes scheduling easy
from airflow.utils.dates import days_ago

# dag arguments
default_args = {
    'owner' : 'Manik',
    'start_date' : days_ago(0),
    'email':'sample@gmail.com',
    'email_on_failure': True,
    'email_on_retry': True,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Dag definition

dag = DAG(
    dag_id = 'ETL_toll_date',
    default_args = default_args,
    description = 'Apache Airflow Assignment',
    schedule_interval =timedelta(days=1),
)

# task unzip data
unzip_data = UnzipOperator(
    task_id = 'unzip_data',
    path_to_zip_file = 'wget "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DB0250EN-SkillsNetwork/labs/Final%20Assignment/tolldata.tgz"'
    path_to_unzip_file = '/home/project/airflow/dags/finalassignment/fileformats.txt'
    dag= dag,

)

# task to extract data from csv file

extract_data_from_csv = BashOperator(
    task_id ='extract_data_from_csv',
    bash_command = 'cut -d":" -f1-4  /home/project/airflow/dags/finalassignment/staging/vehicle-data.csv > /home/project/airflow/dags/finalassignment/staging/csv_data.csv',
    dag = dag,
)

# task to extract data from tsv file
extract_data_from_tsv = BashOperator(
    task_id = 'extract_data_from_tsv',
    bash_command = 'cut -f5-7 /home/project/airflow/dags/finalassignment/staging/tollplaza-data.tsv > /home/project/airflow/dags/finalassignment/staging/tsv_data.csv --output-delimiter=","',
    dag = dag,
)

# task to extract data from fixed width file
extract_data_from_fixed_width = BashOperator(
    task_id = 'extract_data_from_fixed_width'
    bash_command = 'cut -c 59-61, 63-68 /home/project/airflow/dags/finalassignment/staging/payment-data.txt > /home/project/airflow/dags/finalassignment/staging/fixed_width_data.csv --output-delimiter=","',
    dag = dag,
)

# task to consolidate data extracted from previous tasks
consolidate_data = BashOperator(
    task_id = 'consolidate_data'
    bash_command = 'paste /home/project/airflow/dags/finalassignment/staging/csv_data.csv /home/project/airflow/dags/finalassignment/staging/tsv_data.csv /home/project/airflow/dags/finalassignment/staging/fixed_width_data.csv > /home/project/airflow/dags/finalassignment/staging/extracted_data.csv',
    dag = dag,
)

#Task 1.8 - Transform and load the data
transform_data = BashOperator(
    task_id = 'transform_data',
    bash_command = 'tr "[a-z]" "[A-z]" /home/project/airflow/dags/finalassignment/stagingextracted_data.csv > /home/project/airflow/dags/finalassignment/staging/transformed_data.csv'
)

#Task 1.9 - Define the task pipeline
unzip_data >> extract_data_from_csv >> extract_data_from_tsv >> extract_data_from_fixed_width >> consolidate_data >> transform_data