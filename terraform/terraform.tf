terraform {
  cloud {
    organization = "flying_bee"

    workspaces {
      project = "Backend"
      name    = "fly_ing_bee"
    }
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}