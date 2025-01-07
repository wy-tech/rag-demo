provider "aws" {
  region = var.region
}

# Create IAM Role for EC2 instance
resource "aws_iam_role" "rag_ec2_role" {
  name               = "rag-ec2-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action    = "sts:AssumeRole"
        Effect    = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      },
    ]
  })
}

resource "aws_iam_role_policy_attachment" "rag_ec2_ecr_readonly" {
  role       = aws_iam_role.rag_ec2_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}

resource "aws_iam_instance_profile" "ec2_profile" {
  name = "ec2_profile"
  role = var.ec2_iam_role_name
}

# Create security group for EC2 instance
resource "aws_security_group" "rag_sg" {
  name        = "rag-demo-sg"
  description = "Security group for rag demo"

  ingress {
    from_port   = 8501
    to_port     = 8501
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"  # Allow all protocols
    cidr_blocks = ["0.0.0.0/0"]  # Allow all outbound traffic to any destination
  }
}

# Create EC2 instance, attach above security group and iam role
resource "aws_instance" "rag_ec2" {
  instance_type = "t2.micro"
  key_name      = var.KEY_NAME  
  security_groups = [aws_security_group.rag_sg.name]
  iam_instance_profile = aws_iam_instance_profile.ec2_profile.name
  ami = "ami-0995922d49dc9a17d"

  tags = {
    Name = "rag-demo-instance"
  }

  user_data = <<-EOT
  #!/bin/bash
  sudo yum update -y 
  sudo yum -y install docker 
  sudo service docker start 
  sudo usermod -a -G docker ec2-user 
  sudo chmod 666 /var/run/docker.sock 

  aws ecr get-login-password --region "${var.region}" | docker login --username AWS --password-stdin "${var.AWS_ACCOUNT_ID}".dkr.ecr."${var.region}".amazonaws.com
  docker pull "${var.AWS_ACCOUNT_ID}".dkr.ecr."${var.region}".amazonaws.com/rag-demo:latest
  docker tag "${var.AWS_ACCOUNT_ID}".dkr.ecr."${var.region}".amazonaws.com/rag-demo:latest rag-demo:latest
  docker run -p 8501:8501 \
  -e OPENAI_API_KEY="${var.OPENAI_API_KEY}" \
  -e LANGCHAIN_API_KEY="${var.LANGCHAIN_API_KEY}" \
  -e LANGCHAIN_TRACING_V2="${var.LANGCHAIN_TRACING_V2}" \
  -e LANGCHAIN_ENDPOINT="${var.LANGCHAIN_ENDPOINT}" \
  -d --name rag-demo rag-demo:latest
EOT
}
