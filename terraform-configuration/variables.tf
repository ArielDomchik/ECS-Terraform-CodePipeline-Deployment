variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "BG_COLOR"{
  default = [
        {
          "name": "BG_COLOR",
          "value": "black"
        }
      ]
}
