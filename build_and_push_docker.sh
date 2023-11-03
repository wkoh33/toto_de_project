#!/bin/bash

# Get AWS account
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query 'Account' --output text)

# AWS ECR Login
aws ecr get-login-password --region ap-southeast-1 | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.ap-southeast-1.amazonaws.com/toto_project

# Build Docker Image
cd src
docker-compose build

# docker images
images=("toto_load_winning_numbers" "toto_load_winning_outlets" "toto_load_winning_shares")

# tag docker image
for image in "${images[@]}"; do
    docker tag $image:latest $AWS_ACCOUNT_ID.dkr.ecr.ap-southeast-1.amazonaws.com/$image:latest
    docker push $AWS_ACCOUNT_ID.dkr.ecr.ap-southeast-1.amazonaws.com/$image:latest
done

# Clean up: Remove docker images
for image in "${images[@]}"; do
    docker image rm $AWS_ACCOUNT_ID.dkr.ecr.ap-southeast-1.amazonaws.com/$image:latest
    docker image rm $image:latest
done

# Clean up: Logout from AWS ECR
docker logout $AWS_ACCOUNT_ID.dkr.ecr.ap-southeast-1.amazonaws.com