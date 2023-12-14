#!/bin/bash

# Get AWS account
AWS_DEFAULT_PROFILE=toto
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query 'Account' --output text --profile $AWS_DEFAULT_PROFILE)
AWS_REGION=ap-southeast-1

# Check AWS_ACCOUNT_ID is empty
if [ -z "$AWS_ACCOUNT_ID" ]; then
    echo "AWS_ACCOUNT_ID is empty"
    exit 1
fi

# AWS ECR Repo Login
ECR_REPO=$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/toto_project
LOGIN_STATUS=$(aws ecr get-login-password --region $AWS_REGION --profile $AWS_DEFAULT_PROFILE | docker login --username AWS --password-stdin $ECR_REPO)

# Check LOGIN_STATUS is "Login Succeeded"
if [ "$LOGIN_STATUS" != "Login Succeeded" ]; then
    echo "AWS ECR Login Failed"
    exit 1
fi

echo "AWS ECR $LOGIN_STATUS"

# Build Docker Image
echo "Building Docker Image"
cd src
docker-compose build

# docker images
# images=("test_duckdb")
images=("toto_load_winning_numbers" "toto_load_winning_outlets" "toto_load_winning_shares" "test_duckdb")

# tag docker image
for image in "${images[@]}"; do
    docker tag $image:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$image:latest
    docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$image:latest

    aws lambda update-function-code --profile $AWS_DEFAULT_PROFILE --no-cli-pager --function-name $image --image-uri $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$image:latest
done

# Clean up: Remove docker images
for image in "${images[@]}"; do
    docker image rm $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$image:latest
    docker image rm $image:latest
done

# Clean up: Logout from AWS ECR
docker logout $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

echo "Done"