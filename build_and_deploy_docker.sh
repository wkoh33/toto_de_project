#!/bin/bash

# Get AWS account
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query 'Account' --output text)
AWS_REGION=ap-southeast-1

# AWS ECR Login
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/toto_project

# Build Docker Image
cd src
docker-compose build

# docker images
images=("toto_load_winning_numbers" "toto_load_winning_outlets" "toto_load_winning_shares")

# tag docker image
for image in "${images[@]}"; do
    docker tag $image:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$image:latest
    docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$image:latest

    aws lambda update-function-code --no-cli-pager --function-name $image --image-uri $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$image:latest
done

# Clean up: Remove docker images
for image in "${images[@]}"; do
    docker image rm $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$image:latest
    docker image rm $image:latest
done

# Clean up: Logout from AWS ECR
docker logout $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com