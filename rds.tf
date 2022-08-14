resource "aws_db_subnet_group" "database" {
  name       = "${var.project_name}-${var.stage}-database-group"
  subnet_ids = module.vpc.public_subnet_ids

  tags = {
    Name = "${var.project_name}-${var.stage}-database-group"
  }
}

resource "aws_db_instance" "primary" {
  allocated_storage   = var.db_storage
  engine              = "postgres"
  instance_class      = var.db_instance
  username            = var.db_user
  password            = var.db_password
  skip_final_snapshot = true
  iops                = var.db_iops
  db_name             = var.db_name
  publicly_accessible = true

  db_subnet_group_name = aws_db_subnet_group.database.id
  vpc_security_group_ids = [
    module.vpc.postgresql_security_group_id
  ]
}
