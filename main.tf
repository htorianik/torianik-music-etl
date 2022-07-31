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
