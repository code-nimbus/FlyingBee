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

variable "repo_url" {
  description = "URL of the Git repository to clone on the EC2 instance."
  type        = string
  default     = ""
}

variable "gh_pat" {
  description = "GitHub Personal Access Token used to clone the repository."
  type        = string
  sensitive   = true
  default     = ""
}

variable "mail_username" {
  description = "SMTP username used by the application."
  type        = string
  default     = ""
}

variable "mail_password" {
  description = "SMTP password used by the application."
  type        = string
  sensitive   = true
  default     = ""
}

variable "mail_from" {
  description = "Email address used as the sender."
  type        = string
  default     = ""
}

variable "mail_port" {
  description = "SMTP server port."
  type        = number
  default     = 587
}

variable "mail_server" {
  description = "SMTP server hostname."
  type        = string
  default     = ""
}

variable "access_token_expire_minutes" {
  description = "JWT access token expiration time in minutes."
  type        = number
  default     = 30
}

variable "secret_key" {
  description = "Secret key used for application authentication."
  type        = string
  sensitive   = true
  default     = ""
}

variable "algorithm" {
  description = "JWT signing algorithm."
  type        = string
  default     = "HS256"
}

variable "travelpayouts_api_key" {
  description = "Travelpayouts API key."
  type        = string
  sensitive   = true
  default     = ""
}

variable "travelpayouts_marker" {
  description = "Travelpayouts API marker."
  type        = string
  default     = ""
}

variable "travelpayouts_base_url" {
  description = "Base URL for the Travelpayouts API."
  type        = string
  default     = ""
}

variable "duffel_api_token" {
  description = "Duffel API authentication token."
  type        = string
  sensitive   = true
  default     = ""
}