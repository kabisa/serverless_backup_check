
ENV_FILE=environment.sh

if [ -e $ENV_FILE ]; then
  source $ENV_FILE
  echo "Ready to deploy to AWS!"
else
  echo "$ENV_FILE is missing, please add this file containing a line with 'BUCKET_NAME=XXX'!"
fi

