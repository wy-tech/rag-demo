output "ec2_public_ip" {
  value = aws_instance.rag_ec2.public_ip
}