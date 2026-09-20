# python-test

This project contains source code and supporting files for a serverless application to deploy with the SAM CLI. It includes the following files and folders.

- hello_world - Code for the application's Lambda function.
- events - Invocation events that you can use to invoke the function.
- tests - Unit tests for the application code. 
- template.yaml - A template that defines the application's AWS resources.

## Python Virtual Env

### Setup
```bash
pyenv virtualenv 3.12.7 aws-sam-cli-3.12.7
pip install aws-sam-cli
```

### Use

```bash
pyenv activate aws-sam-cli-3.12.7
```

## Deploy the sample application

### Setup local env

Add Allowed IP Address range to `.env` for aws api access

```bash
ALLOWED_IP_ADDRESS="1.2.3.4/32"
```

### Build and Deploy

```bash
sam build --use-container
./deploy.sh
```

### test locally

Execute handler:

```bash
sam local invoke HelloWorldFunction --event events/event.json
```

for Address calls:

```bash
sam local start-api
curl http://localhost:3000/
```

## Fetch, tail, and filter Lambda function logs

```bash
$ sam logs -n HelloWorldFunction --stack-name "python-test" --tail
```

## Tests

```bash
$ pip install -r tests/requirements.txt
# unit test
$ python -m pytest tests/unit -v
# integration test, requiring deploying the stack first.
$ AWS_SAM_STACK_NAME="python-test" python -m pytest tests/integration -v
```

## Cleanup

To delete the sample application that you created, use the AWS CLI. Assuming you used your project name for the stack name, you can run the following:

```bash
sam delete --stack-name "python-test"
```