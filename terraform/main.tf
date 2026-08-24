provider "aws" {
  region = "ap-south-1"
}

data "aws_ami" "ubuntu" {
  most_recent = true

  owners = ["099720109477"] # Canonical

}

resource "aws_instance" "app_server" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = var.instance_type

  vpc_security_group_ids = [aws_security_group.app_server_sg.id]
  subnet_id              = module.vpc.public_subnets[0]

  tags = {
    Name = var.instance_name
  }
}

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "6.0"

  name = "flyingbee-app-server"
  cidr = "10.0.0.0/16"

  azs             = ["ap-south-1a", "ap-south-1b", "ap-south-1c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
  public_subnets  = ["10.0.101.0/24"]

  enable_dns_hostnames = true
}

resource "aws_security_group" "app_server_sg" {
  name        = "app-server-sg"
  description = "Allow inbound traffic on port 80"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}