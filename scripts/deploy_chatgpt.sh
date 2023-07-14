#!/bin/sh

set -o errexit
# set -o xtrace #for debug purposes
set -o pipefail
set -o nounset

# LAMBDA="$1"
# TAG="$2"
# TAG_RETRY="$TAG-retry"
# ENVIRONMENT="$3"
LAMBDA="wizeline-generative-chatgpt"
TAG="latest"
# TAG_RETRY="$TAG-retry"
ENVIRONMENT="sandbox"
REGION="us-east-1"
REGISTRY="689813869550.dkr.ecr.us-east-1.amazonaws.com"

set -o allexport
# source .$ENVIRONMENT.env
set +o allexport

# As per this link https://tomgregory.com/jenkins-assume-role-in-another-aws-account/ sts assume-role output need to be exported as environment variables
# ASSUME_ROLE_OUTPUT=$(aws sts assume-role --role-arn $DEPLOY_ROLE_ARN --role-session-name $ROLE_SESSION_NAME)
# ASSUME_ROLE_ENVIRONMENT=$(echo $ASSUME_ROLE_OUTPUT | jq -r '.Credentials | .["AWS_ACCESS_KEY_ID"] = .AccessKeyId | .["AWS_SECRET_ACCESS_KEY"] = .SecretAccessKey | .["AWS_SESSION_TOKEN"] = .SessionToken | del(.AccessKeyId, .SecretAccessKey, .SessionToken, .Expiration)
#   | to_entries[] | "export \(.key)=\(.value)"')
# eval $ASSUME_ROLE_ENVIRONMENT
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $REGISTRY

cd lambdas/chatgpt
IMAGE_NAME="$LAMBDA"

echo "🚧 Building ${IMAGE_NAME}:$TAG"
docker build -t $IMAGE_NAME . -f Dockerfile
docker tag $IMAGE_NAME:latest $REGISTRY/$IMAGE_NAME:$TAG

echo "🚧 Pushing $REGISTRY/$IMAGE_NAME:$TAG to ECR"
docker push $REGISTRY/$IMAGE_NAME:$TAG


echo "🚧 Deploying $IMAGE_NAME to AWS Lambda"
aws lambda update-function-code --region $REGION --function-name $IMAGE_NAME --image-uri $REGISTRY/$IMAGE_NAME:$TAG
echo "🏁 Lambda function $IMAGE_NAME deployed successfully 🏁"
