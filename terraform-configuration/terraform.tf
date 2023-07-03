terraform {
  cloud {
    workspaces {
      name = "ecs-project"
    }
  }

  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = "4.45.0"
    }
  }
}
