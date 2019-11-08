while getopts u:p:a: option
do
case "${option}"
in
u) USER=${OPTARG};;
p) PASSWORD=${OPTARG};;
a) APIKEY=${OPTARG};;
esac
done

if [ -z "$USER" ] || [ -z "$PASSWORD" ] || [ -z "$APIKEY" ]
then
      echo "you must specify all the parameters -u(user) -p(passowrd) -a(apikey)"
      exit
fi

if ! [ -x "$(command -v virtualenv)" ] || ! [ -x "$(command -v aws)" ] || ! [ -x "$(command -v python3)" ]
then
  echo 'you must have installed virtualenv, python, aws cli' >&2
  exit 1
fi

echo "creating bucket"
aws cloudformation deploy --template-file bucket-template.yaml --stack-name s3-bucket-avengers
bucket_name=$(aws cloudformation describe-stacks --stack-name s3-bucket-avengers --query 'Stacks[0].Outputs[0].OutputValue' --output text)
echo "creating the lambda layer"
mkdir -p helpers/python
cp -r avengers/helpers helpers/python/
virtualenv -p python3 venv
source venv/bin/activate
pip install --target ./helpers/python -r requirements.txt

echo "Packaging templates..."
aws cloudformation package --template-file api-template.yaml --output-template-file api-template-export.yaml --s3-bucket ${bucket_name}
echo "Uploading export templates to s3..."
aws s3 cp api-template-export.yaml s3://${bucket_name}/templates/api-template-export.yaml
echo "Cleaning up.."
rm api-template-export.yaml
echo "Packaging templates..."
aws cloudformation package --template-file db-template.yaml --output-template-file db-template-export.yaml --s3-bucket ${bucket_name}
echo "Uploading export templates to s3..."
aws s3 cp db-template-export.yaml s3://${bucket_name}/templates/db-template-export.yaml
echo "Cleaning up.."
rm db-template-export.yaml
echo "Packaging templates..."
aws cloudformation package --template-file dynamo-template.yaml --output-template-file dynamo-template-export.yaml --s3-bucket ${bucket_name}
echo "Uploading export templates to s3..."
aws s3 cp dynamo-template-export.yaml s3://${bucket_name}/templates/dynamo-template-export.yaml
echo "Cleaning up.."
rm dynamo-template-export.yaml
echo "Packaging templates..."
aws cloudformation package --template-file etl-template.yaml --output-template-file etl-template-export.yaml --s3-bucket ${bucket_name}
echo "Uploading export templates to s3..."
aws s3 cp etl-template-export.yaml s3://${bucket_name}/templates/etl-template-export.yaml
echo "Cleaning up.."
rm etl-template-export.yaml
echo "Packaging templates..."
aws cloudformation package --template-file layer-template.yaml --output-template-file layer-template-export.yaml --s3-bucket ${bucket_name}
echo "Uploading export templates to s3..."
aws s3 cp layer-template-export.yaml s3://${bucket_name}/templates/layer-template-export.yaml
echo "Cleaning up.."
rm layer-template-export.yaml
echo "Packaging templates..."
aws cloudformation package --template-file vpc-template.yaml --output-template-file vpc-template-export.yaml --s3-bucket ${bucket_name}
echo "Uploading export templates to s3..."
aws s3 cp vpc-template-export.yaml s3://${bucket_name}/templates/vpc-template-export.yaml
echo "Cleaning up.."
rm vpc-template-export.yaml
echo "deploying in cloudformation"
aws cloudformation deploy --template-file master-template.yaml --stack-name avengers-assemble --capabilities CAPABILITY_IAM CAPABILITY_AUTO_EXPAND --parameter-overrides BucketFiles=${bucket_name} DBUsername=${USER} DBPassword=${PASSWORD} APIKey=${APIKEY}

echo "creating the tables"
aws lambda invoke --function-name crete-tables-avengers --payload '{}' response.json
cd avengers
echo "kickoff"
export APIKEY
python ./genesis/kickoff.py

aws s3 cp creators.p s3://${bucket_name}/creators/genesis.p
aws s3 cp comics.p s3://${bucket_name}/comics/genesis.p
aws s3 cp creator_comic.p s3://${bucket_name}/creator_comic/genesis.p
aws s3 cp characters.p s3://${bucket_name}/characters/genesis.p
aws s3 cp target_characters.p s3://${bucket_name}/target_characters/genesis.p
aws s3 cp comic_character.p s3://${bucket_name}/comic_character/genesis.p

echo "populating db"
aws lambda invoke --function-name upsertDfPostgres --payload '{"file_type":"creators", "str_date": "genesis"}' response.json
aws lambda invoke --function-name upsertDfPostgres --payload '{"file_type":"comics", "str_date": "genesis"}' response.json
aws lambda invoke --function-name upsertDfPostgres --payload '{"file_type":"creator_comic", "str_date": "genesis"}' response.json
aws lambda invoke --function-name upsertDfPostgres --payload '{"file_type":"characters", "str_date": "genesis"}' response.json
aws lambda invoke --function-name upsertDfPostgres --payload '{"file_type":"target_characters", "str_date": "genesis"}' response.json
aws lambda invoke --function-name upsertDfPostgres --payload '{"file_type":"comic_character", "str_date": "genesis"}' response.json
