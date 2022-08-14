resource "aws_s3_bucket" "data_lake" {
  bucket = "${var.account_id}-${var.project_name}-${var.stage}-data-lake"

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_s3_bucket_public_access_block" "data_lake" {
  bucket = aws_s3_bucket.data_lake.id

  block_public_acls   = true
  block_public_policy = true
}

resource "aws_s3_bucket" "sources" {
  bucket = "${var.account_id}-${var.project_name}-${var.stage}-sources"
}

resource "aws_s3_bucket_versioning" "sources" {
  bucket = aws_s3_bucket.sources.bucket
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_public_access_block" "sources" {
  bucket = aws_s3_bucket.sources.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket" "temp" {
  bucket = "${var.account_id}-${var.project_name}-${var.stage}-temp"
}

resource "aws_s3_bucket_public_access_block" "temp" {
  bucket = aws_s3_bucket.temp.id

  block_public_acls   = true
  block_public_policy = true
}

locals {
  sources = [
    "clean.py",
    "load_artists.py",
    "load_edges.py",
    "load_playlists.py",
    "load_tracks.py",
    "create_tables.sql",
    "airflow/requirements.txt",
    "airflow/dags/torianik_music_etl.py",
  ]
}

resource "aws_s3_object" "source_file" {
  for_each = toset(local.sources)

  bucket = aws_s3_bucket.sources.id

  key    = each.key
  source = "resources/${each.key}"

  etag = md5(file("resources/${each.key}")) # terraform<=0.11.11 legacy
}
