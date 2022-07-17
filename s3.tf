resource "aws_s3_bucket" "data_lake" {
  bucket = "${var.account_id}-${var.project_name}-${var.stage}-data-lake"
}

resource "aws_s3_bucket_public_access_block" "data_lake" {
  bucket = aws_s3_bucket.data_lake.id

  block_public_acls   = true
  block_public_policy = true
}

resource "aws_s3_bucket" "sources" {
  bucket = "${var.account_id}-${var.project_name}-${var.stage}-sources"
}

resource "aws_s3_bucket_public_access_block" "sources" {
  bucket = aws_s3_bucket.data_lake.id

  block_public_acls   = true
  block_public_policy = true
}

locals {
  etl_job_s3_key = "etl_job.py"
  create_tables_s3_key = "create_tables.sql"
}


resource "aws_s3_object" "etl_job" {
  bucket = aws_s3_bucket.sources.id

  key    = local.etl_job_s3_key
  source = "resources/etl_job.py"

  etag = md5(file("resources/etl_job.py")) # terraform<=0.11.11 legacy
}

resource "aws_s3_object" "create_tables" {
  bucket = aws_s3_bucket.sources.id

  key    = local.create_tables_s3_key
  source = "resources/create_tables.sql"

  etag = md5(file("resources/create_tables.sql")) # terraform<=0.11.11 legacy
}
