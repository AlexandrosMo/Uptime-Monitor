output "ec2_public_ip" { value = aws_instance.app.public_ip }
output "app_url"       { value = "http://${aws_instance.app.public_dns}:80" }
output "ecr_repository_url" { value = aws_ecr_repository.repo.repository_url }
