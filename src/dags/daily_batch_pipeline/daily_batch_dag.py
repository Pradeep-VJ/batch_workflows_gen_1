from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

# Default arguments
default_args = {
    'owner': 'data_engineer',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
}

# DAG definition
with DAG(
    dag_id='emr_s3_data_pipeline',
    default_args=default_args,
    description='Data pipeline using EMR, Spark, and S3',
    schedule_interval='@daily',
    start_date=datetime(2023, 12, 1),
    catchup=False,
) as dag:

    # Create EMR cluster
    create_emr_cluster = BashOperator(
        task_id='create_emr_cluster',
        bash_command="""
        aws emr create-cluster \
        --name "data-processing-cluster" \
        --release-label emr-6.12.0 \
        --applications Name=Spark \
        --ec2-attributes InstanceProfile=EMR_EC2_DefaultRole,SubnetId=subnet-12345678 \
        --instance-groups '[{"InstanceCount":1,"InstanceGroupType":"MASTER","InstanceType":"m5.xlarge"},{"InstanceCount":2,"InstanceGroupType":"CORE","InstanceType":"m5.xlarge"}]' \
        --log-uri "s3://emr-logs-bucket/logs/" \
        --bootstrap-actions Path="s3://bootstrap-bucket/emr_bootstrap.sh" \
        --use-default-roles
        """
    )

    # Submit Spark job
    submit_spark_job = BashOperator(
        task_id='submit_spark_job',
        bash_command="""
        aws emr add-steps \
        --cluster-id {{ ti.xcom_pull(task_ids='create_emr_cluster') }} \
        --steps '[{
          "Name":"SparkTransformationStep",
          "ActionOnFailure":"TERMINATE_CLUSTER",
          "HadoopJarStep":{
            "Jar":"command-runner.jar",
            "Args":["spark-submit","s3://code-bucket/spark_workflow.py"]
          }
        }]'
        """
    )

    # Terminate EMR cluster
    terminate_emr_cluster = BashOperator(
        task_id='terminate_emr_cluster',
        bash_command="""
        aws emr terminate-clusters --cluster-ids {{ ti.xcom_pull(task_ids='create_emr_cluster') }}
        """
    )

    # DAG dependencies
    create_emr_cluster >> submit_spark_job >> terminate_emr_cluster
