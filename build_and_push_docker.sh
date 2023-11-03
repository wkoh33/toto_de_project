#!/bin/bash

# Get AWS account
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query 'Account' --output text)

# AWS ECR Login
aws ecr get-login-password --region ap-southeast-1 | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.ap-southeast-1.amazonaws.com/toto_project

# Build Docker Image
cd src
docker-compose build

# docker images
images=("load_winning_numbers" "load_winning_outlets" "load_winning_shares")

# tag docker image
for image in "${images[@]}"; do
    docker tag $image:latest $AWS_ACCOUNT_ID.dkr.ecr.ap-southeast-1.amazonaws.com/toto_project:$image
    docker push $AWS_ACCOUNT_ID.dkr.ecr.ap-southeast-1.amazonaws.com/toto_project:$image
done

# Clean up: Logout from AWS ECR
docker logout $AWS_ACCOUNT_ID.dkr.ecr.ap-southeast-1.amazonaws.com