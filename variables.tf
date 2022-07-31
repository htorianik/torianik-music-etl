variable "account_id" {
  type        = string
  description = "Identifier of a target AWS account."
}

variable "project_name" {
  type        = string
  description = "Name of a project. Used to add it as a prefix for resource names."
  default     = "torianik-music"
}

variable "stage" {
  type        = string
  description = "Stage of the application."
  default     = "dev"
}

variable "vpc_id" {
  type        = string
  description = "VPC to run the infrastructure in. DNS Hostnames enabled is required"
}

variable "base_cidr_block" {
  type        = string
  description = "CIDR block to put subnets to. At least 16 bits is required."
}

variable "db_user" {
  type        = string
  description = "Database user."
  default     = "postgres"
}

variable "db_password" {
  type        = string
  description = "Database password."
}

variable "db_name" {
  type        = string
  description = "Name of a PostgreSQL database."
  default     = "main"
}

variable "db_instance" {
  type        = string
  description = "Instance type of RDS."
  default     = "db.t3.medium"
}

variable "db_iops" {
  type        = number
  description = "IOPS of the instance."
  default     = 2000
}

variable "db_storage" {
  type        = string
  description = "Size of allocated storage for RDS in Gb."
  default     = 100
}

output "db_conn_url" {
  description = "URL with postgreSQL connection to the target database. This format can be used with SQLAlchemy."
  value       = "postgres://${var.db_user}:${var.db_password}@${aws_db_instance.primary.address}/${var.db_name}"
}

output "data_lake" {
  description = "Uri poiting to data lake s3 bucket."
  value       = "s3://${aws_s3_bucket.data_lake.id}"
}