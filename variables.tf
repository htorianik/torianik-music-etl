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

variable "subnet_id" {
  type        = string
  description = "Private subnet to create RDS Instance, Glue Connection in. NAT is required."
}

variable "secondary_subnet_id" {
  type        = string
  description = "Subnet to create RDS Instance in. Required to be in other availability zone then the primary one."
}

variable "security_group_id" {
  type        = string
  description = "Security group to run RDS and Glue Connection in."
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
  default     = "db.t3.micro"
}

variable "db_storage" {
  type        = string
  description = "Size of allocated storage for RDS in Gb."
  default     = 20
}
