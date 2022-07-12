resource "aws_iam_role" "glue" {
  name = "${var.project_name}-${var.stage}-glue"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          Service = "glue.amazonaws.com"
        }
      },
    ]
  })
}

resource "aws_iam_role_policy" "data_lake" {
  name = "${var.project_name}-${var.stage}-data-lake"
  role = aws_iam_role.glue.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:GetObject",
          "s3:PutObject"
        ]
        Effect = "Allow"
        Resource = [
          "arn:aws:s3:::${aws_s3_bucket.data_lake.id}",
          "arn:aws:s3:::${aws_s3_bucket.data_lake.id}/*",
        ]
      },
    ]
  })
}

resource "aws_iam_role_policy_attachment" "attach-aws-glue-service-role" {
  role       = aws_iam_role.glue.id
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
}
