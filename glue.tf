locals {
  catalog_database_name = "${var.project_name}-${var.stage}-database"
  glue_connection_name  = "${var.project_name}-${var.stage}-postgres-connection"
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

resource "aws_glue_catalog_database" "primary" {
  name = local.catalog_database_name
}

resource "aws_glue_classifier" "spotify_playlists_json" {
  name = "${var.project_name}-${var.stage}-spotify-playlists-json"

  json_classifier {
    json_path = "$.playlists[*]"
  }
}

resource "aws_glue_crawler" "raw" {
  name          = "${var.project_name}-${var.stage}-crawler-raw"
  database_name = aws_glue_catalog_database.primary.name
  role          = aws_iam_role.glue.arn

  s3_target {
    path = "s3://${aws_s3_bucket.data_lake.bucket}/raw/"
  }

  classifiers = [
    aws_glue_classifier.spotify_playlists_json.id
  ]
}

resource "aws_glue_crawler" "clean" {
  name          = "${var.project_name}-${var.stage}-crawler-clean"
  database_name = aws_glue_catalog_database.primary.name
  role          = aws_iam_role.glue.arn

  s3_target {
    path = "s3://${aws_s3_bucket.data_lake.bucket}/clean/"
  }
}

locals {
  jobs = {
    # Name           Script file in sources bucket
    clean          = "clean.py"
    load_artists   = "load_artists.py"
    load_edges     = "load_edges.py"
    load_playlists = "load_playlists.py"
    load_tracks    = "load_tracks.py"
  }
}

resource "aws_glue_job" "etl_job" {
  for_each = local.jobs

  name              = "${var.project_name}-${var.stage}-${each.key}"
  role_arn          = aws_iam_role.glue.arn
  glue_version      = "3.0"
  number_of_workers = 10
  worker_type       = "G.1X"

  command {
    script_location = "s3://${aws_s3_bucket.sources.bucket}/${each.value}"
    python_version  = 3
  }

  non_overridable_arguments = {
    "--job-language"              = "python"
    "--additional-python-modules" = "boto3==1.24.19,ssm-cache==2.10,psycopg2-binary==2.9.3"
  }
}