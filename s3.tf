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

resource "aws_s3_object" "etl_job" {
  bucket = aws_s3_bucket.sources.id

  key    = "etl_job.py"
  source = "resources/etl_job.py"

  etag = "${md5(file("resources/etl_job.py"))}"  # terraform<=0.11.11 legacy
}