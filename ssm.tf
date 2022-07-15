locals {
    ssm_prefix = "${var.project_name}/${var.stage}/"
}

resource "aws_ssm_parameter" "glue_connection_name" {
  name  = "${local.ssm_prefix}glue_connection_name"
  type  = "String"
  value = local.glue_connection_name
}

resource "aws_ssm_parameter" "catalog_database_name" {
  name  = "${local.ssm_prefix}catalog_database_name"
  type  = "String"
  value = local.catalog_database_name
}

resource "aws_ssm_parameter" "database_name" {
  name  = "${local.ssm_prefix}database_name"
  type  = "String"
  value = var.db_name
}