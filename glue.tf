resource "aws_glue_catalog_database" "primary" {
  name = "${var.project_name}-${var.stage}-database"
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

resource "aws_glue_connection" "primary" {
  name = "${var.project_name}-${var.stage}-postgres-connection"

  connection_properties = {
    JDBC_CONNECTION_URL = "jdbc:postgresql://${aws_db_instance.primary.endpoint}/${var.db_name}"
    USERNAME            = var.db_user
    PASSWORD            = var.db_password
  }

  physical_connection_requirements {
    subnet_id = data.aws_subnet.primary.id

    availability_zone = data.aws_subnet.primary.availability_zone

    security_group_id_list = [
      var.security_group_id
    ]
  }
}

resource "aws_glue_job" "primary" {
  name         = "${var.project_name}-${var.stage}-etl-job"
  role_arn     = aws_iam_role.glue.arn
  glue_version = "3.0"

  command {
    script_location = "s3://${aws_s3_bucket.sources.bucket}/${local.etl_job_s3_key}"
  }
}