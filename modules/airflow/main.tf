resource "aws_mwaa_environment" "primary" {
    dag_s3_path = "airflow/dags/"
    execution_role_arn = "add me"
    name = "${var.project_name}-${var.stage}-mwaa-env"
}