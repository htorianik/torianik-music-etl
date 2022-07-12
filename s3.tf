resource "aws_s3_bucket" "data_lake" {
  bucket = "${var.account_id}-${var.project_name}-${var.stage}-data-lake"
}

resource "aws_s3_bucket_public_access_block" "data_lake" {
  bucket = aws_s3_bucket.data_lake.id

  block_public_acls   = true
  block_public_policy = true
}
