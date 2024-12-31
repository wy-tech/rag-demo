docker build -t rag-demo -f Dockerfile .

aws ecr get-login-password --region "${AWS_REGION}" | docker login --username AWS --password-stdin "${AWS_ACCOUNT_ID}".dkr.ecr."${AWS_REGION}".amazonaws.com
docker tag rag-demo "${AWS_ACCOUNT_ID}".dkr.ecr."${AWS_REGION}".amazonaws.com/rag-demo:latest
docker push "${AWS_ACCOUNT_ID}".dkr.ecr."${AWS_REGION}".amazonaws.com/rag-demo:latest