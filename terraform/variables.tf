variable "region" {
    description = "Name of the IAM role to attach to EC2 instance"
    default = "ap-southeast-1"
    type = string
}

variable "ec2_iam_role_name" {
    description = "Name of the IAM role to attach to EC2 instance"
    default = "rag-ec2-role"
    type = string
}

variable "KEY_NAME" {
  description = "key name for ssh"
  type        = string
}

variable "AWS_ACCOUNT_ID" {
  description = "AWS account ID"
  type        = string
}

variable "OPENAI_API_KEY" {
  description = "OpenAI API key"
  type        = string
}

variable "LANGCHAIN_TRACING_V2" {
  description = "Langchain tracing for logging to langsmith"
  default = "true" 
  type = string
}

variable "LANGCHAIN_ENDPOINT" {
  description = "Langchain endpoint for logging to langsmith"
  default = "https://api.smith.langchain.com" 
  type = string
}

variable "LANGCHAIN_API_KEY" {
  description = "Langchain API key for logging to langsmith"
  type = string
}
