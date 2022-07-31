variable "project_name" {
  type        = string
  description = "Name of a project. Used to add it as a prefix for resource names."
}

variable "stage" {
  type        = string
  description = "Stage of the application."
}

variable "vpc_id" {
  type        = string
  description = "VPC to run the infrastructure in."
}

variable "base_cidr_block" {
  type        = string
  description = "CIDR block to put subnets to. At least 16 bits is required."
}