locals {
    ssm_prefix = "/${var.project_name}/${var.stage}/"
}

resource "aws_ssm_parameter" "glue_connection_name" {
  name  = "${local.ssm_prefix}glue_connection_name"
  type  = "String"
  value = local.glue_connection_name
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

resource "aws_ssm_parameter" "database_user" {
  name  = "${local.ssm_prefix}database_user"
  type  = "String"
  value = var.db_user
}

resource "aws_ssm_parameter" "database_password" {
  name  = "${local.ssm_prefix}database_password"
  type  = "SecureString"
  value = var.db_password
}

resource "aws_ssm_parameter" "database_host" {
  name  = "${local.ssm_prefix}database_host"
  type  = "String"
  value = aws_db_instance.primary.address
}

resource "aws_ssm_parameter" "sources_bucket" {
  name  = "${local.ssm_prefix}sources_bucket"
  type  = "String"
  value = aws_s3_bucket.sources.id
}
