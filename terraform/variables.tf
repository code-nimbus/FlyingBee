variable "instance_name" {
  description = "Value of the EC2 instance's name tag"
  type        = string
  default     = "flyingbee-app-server"
}

variable "instance_type" {
  description = "The EC2 instance's name tag"
  type        = string
  default     = "t4g.micro"
}