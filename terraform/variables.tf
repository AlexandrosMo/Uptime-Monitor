variable "project_name" { type = string  default = "uptime-monitor" }
variable "region"       { type = string  default = "eu-central-1" }
variable "instance_type"{ type = string  default = "t3.micro" }
variable "key_name"     { type = string  description = "Existing EC2 key pair name" }
variable "allowed_cidr" { type = string  default = "0.0.0.0/0" }
