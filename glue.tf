locals {
  catalog_database_name = "${var.project_name}-${var.stage}-database"
  glue_connection_name = "${var.project_name}-${var.stage}-postgres-connection"
}

resource "aws_glue_catalog_database" "primary" {
  name = local.catalog_database_name
}

resource "aws_glue_classifier" "spotify_playlists_json" {
  name = "${var.project_name}-${var.stage}-spotify-playlists-json"

  json_classifier {
    json_path = "$.playlists[*]"
  }
}

resource "aws_glue_crawler" "primary" {
  name          = "${var.project_name}-${var.stage}-crawler"
  database_name = aws_glue_catalog_database.primary.name
  role          = aws_iam_role.glue.arn

  s3_target {
    path = "s3://${aws_s3_bucket.data_lake.bucket}"
  }

  classifiers = [
    aws_glue_classifier.spotify_playlists_json.id
  ]
}

resource "aws_glue_job" "primary" {
  name         = "${var.project_name}-${var.stage}-etl-job"
  role_arn     = aws_iam_role.glue.arn
  glue_version = "3.0"

  command {
    script_location = "s3://${aws_s3_bucket.sources.bucket}/${local.etl_job_s3_key}"
    python_version = 3
  }

  non_overridable_arguments = {
    "--job-language" = "python"
    "--additional-python-modules" = "boto3==1.24.19,ssm-cache==2.10,psycopg2-binary==2.9.3"
  }
}