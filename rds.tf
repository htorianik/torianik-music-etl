resource "aws_db_subnet_group" "database" {
  name = "${var.project_name}-${var.stage}-database-group"
  subnet_ids = [
    data.aws_subnet.primary.id,
    data.aws_subnet.secondary.id
  ]

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
  db_name             = var.db_name
  publicly_accessible = true

  db_subnet_group_name = aws_db_subnet_group.database.id
  vpc_security_group_ids = [
    var.security_group_id
  ]
}

resource "null_resource" "db_setup" {

  depends_on = [aws_db_instance.primary]

  provisioner "local-exec" {
    command = <<EOT
        psql \
            --host=${aws_db_instance.primary.address} \
            --port=${aws_db_instance.primary.port} \
            --user=${var.db_user} \
            --file=resources/schema.sql
        EOT
    environment = {
      PGPASSWORD = var.db_password
    }
  }
}
