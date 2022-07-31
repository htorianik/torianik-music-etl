module "subnet_addrs" {
  source = "hashicorp/subnets/cidr"

  base_cidr_block = var.base_cidr_block
  networks = [
    {
      name     = "${var.project_name}-${var.stage}-public-us-east-1a"
      new_bits = 8
    },
    {
      name     = "${var.project_name}-${var.stage}-public-us-east-1b"
      new_bits = 8
    },
    {
      name     = "${var.project_name}-${var.stage}-private-us-east-1a"
      new_bits = 8
    },
    {
      name     = "${var.project_name}-${var.stage}-private-us-east-1b"
      new_bits = 8
    },
  ]
}

locals {
  public_subnets = {
    "us-east-1a" = module.subnet_addrs.networks[0]
    "us-east-1b" = module.subnet_addrs.networks[1]
  }

  private_subnets = {
    "us-east-1a" = module.subnet_addrs.networks[2]
    "us-east-1b" = module.subnet_addrs.networks[3]
  }
}


resource "aws_internet_gateway" "mod" {
  vpc_id = var.vpc_id
  tags = {
    Name = "${var.project_name}-${var.stage}-igw"
  }
}

resource "aws_route_table" "public" {
  vpc_id = var.vpc_id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.mod.id
  }

  tags = {
    Name = "${var.project_name}-${var.stage}-rt-public"
  }
}

resource "aws_route_table" "private" {
  for_each = local.private_subnets

  vpc_id = var.vpc_id
  tags = {
    Name = "${var.project_name}-${var.stage}-rt-private"
  }
}

resource "aws_subnet" "private" {
  for_each = local.private_subnets

  vpc_id = var.vpc_id
  cidr_block = each.value.cidr_block
  availability_zone = each.key
  tags = {
    Name = "${var.project_name}-${var.stage}-${each.key}-private"
  }
}

resource "aws_subnet" "public" {
  for_each = local.public_subnets

  vpc_id = var.vpc_id
  cidr_block = each.value.cidr_block
  availability_zone = each.key
  map_public_ip_on_launch = true

  tags = {
    Name = "${var.project_name}-${var.stage}-${each.key}-public"
  }
}

resource "aws_route_table_association" "private" {
  for_each = local.private_subnets

  subnet_id = aws_subnet.private[each.key].id
  route_table_id = aws_route_table.private[each.key].id
}

resource "aws_route_table_association" "public" {
  for_each = local.public_subnets

  subnet_id = aws_subnet.public[each.key].id
  route_table_id = aws_route_table.public.id
}

# Nat Gateway

resource "aws_eip" "nat" {
  for_each = local.private_subnets

  vpc   = true
}

resource "aws_nat_gateway" "nat" {
  for_each = local.private_subnets

  allocation_id = aws_eip.nat[each.key].id
  subnet_id     = aws_subnet.private[each.key].id
}

resource "aws_route" "nat_gateway" {
  for_each               = local.private_subnets

  route_table_id         = aws_route_table.private[each.key].id
  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id         = aws_nat_gateway.nat[each.key].id

  depends_on             = [
    aws_route_table.private
  ]
}

# Securty Groups

resource "aws_security_group" "allow_postgresql" {
  name        = "${var.project_name}-${var.stage}-sg-allow-postgresql"
  description = "Allow PostgreSQL inbound traffic"
  vpc_id      = var.vpc_id

  ingress {
    description      = "PostgreSQL from the Internet"
    from_port        = 5432
    to_port          = 5432
    protocol         = "tcp"
    cidr_blocks      = ["0.0.0.0/0"]
  }

  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-${var.stage}-sg-allow-postgresql"
  }
}

resource "aws_security_group" "glue_connection" {
  name        = "${var.project_name}-${var.stage}-sg-glue-connection"
  description = "Segurity group for the glue connection"
  vpc_id      = var.vpc_id

  ingress {
    description      = "PostgreSQL from the Internet"
    from_port        = 0
    to_port          = 65535
    protocol         = "tcp"
    cidr_blocks      = ["0.0.0.0/0"]
  }

  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-${var.stage}-sg-glue-connection"
  }
}