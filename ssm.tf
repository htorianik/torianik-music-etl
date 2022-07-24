locals {
  ssm_prefix = "/${var.project_name}/${var.stage}/"
}

resource "aws_ssm_parameter" "glue_connection" {
  name  = "${local.ssm_prefix}glue_connection"
  type  = "String"
  value = aws_glue_connection.primary.name
}

resource "aws_ssm_parameter" "catalog_database" {
  name  = "${local.ssm_prefix}catalog_database"
  type  = "String"
  value = local.catalog_database_name
}

resource "aws_ssm_parameter" "database_name" {
  name  = "${local.ssm_prefix}database_name"
  type  = "String"
  value = var.db_name
}

locals {
  ssm_buckets = {
    # SSM param name   # Bucket name
    temp_bucket      = aws_s3_bucket.temp.id
    sources_bucket   = aws_s3_bucket.sources.id
    data_lake_bucket = aws_s3_bucket.data_lake.id
  }
}

resource "aws_ssm_parameter" "bucket_ssm" {
  for_each = local.ssm_buckets

  name  = "${local.ssm_prefix}${each.key}"
  type  = "String"
  value = each.value
}
