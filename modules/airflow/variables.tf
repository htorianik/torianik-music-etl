variable "project_name" {
  type        = string
  description = "Name of a project. Used to add it as a prefix for resource names."
}

variable "stage" {
  type        = string
  description = "Stage of the application."
}