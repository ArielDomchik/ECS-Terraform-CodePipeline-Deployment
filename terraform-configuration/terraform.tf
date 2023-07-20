terraform {
  cloud {
    workspaces {
      name = "<your-backend-here>"
    }
  }

  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = "4.45.0"
    }
  }
}
