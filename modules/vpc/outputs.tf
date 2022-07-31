output "public_subnets" {
    value = aws_subnet.public
    description = "Public subnets."
}

output "private_subnets" {
    value = aws_subnet.private
    description = "Private subnets."
}

output "public_subnet_ids" {
    value = [for subnet in aws_subnet.public: subnet.id]
    description = "Identifiers of public subnets."
}

output "private_subnet_ids" {
    value = [for subnet in aws_subnet.private: subnet.id]
    description = "Identifiers of private subnets."
}

output "postgresql_security_group_id" {
    value = aws_security_group.allow_postgresql.id
    description = "Identifier of a security group that allows inbound PostgreSQL traffic."
}

output "glue_connection_security_group_id" {
    value = aws_security_group.glue_connection.id
    description = "Identifier of a security group that allows glue connection to reach the db instance."
}