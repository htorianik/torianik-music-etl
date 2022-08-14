terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }

    null = {
      source  = "hashicorp/null"
      version = "~> 3.1"
    }
  }

  required_version = ">= 1.1.0"

  backend "s3" {
    bucket = "torianik-music-etl-terraform-state-ue1"
    key    = "tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = "us-east-1"
}

module "vpc" {
  source = "./modules/vpc"

  project_name    = var.project_name
  stage           = var.stage
  vpc_id          = var.vpc_id
  base_cidr_block = var.base_cidr_block
}

/*
module "airflow" {
  source = "idealo/mwaa/aws"

  create_networking_config = false
  account_id               = data.aws_caller_identity.current.account_id
  environment_name         = var.stage
  internet_gateway_id      = module.vpc.internet_gateway_id
  private_subnet_ids       = module.vpc.private_subnet_ids
  region                   = "us-east-1"
  vpc_id                   = var.vpc_id

  source_bucket_arn    = aws_s3_bucket.sources.arn
  dag_s3_path          = "airflow/dags/"
  requirements_s3_path = "airflow/requirements.txt"
}
*/
