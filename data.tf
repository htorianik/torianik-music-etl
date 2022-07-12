data "aws_subnet" "primary" {
    id = var.subnet_id
}

data "aws_subnet" "secondary" {
    id = var.secondary_subnet_id
}