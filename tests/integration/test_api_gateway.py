import os
import boto3
import pytest
import requests

"""
Make sure env variable AWS_SAM_STACK_NAME exists with the name of the stack we are going to test.

To run these tests:
    export AWS_SAM_STACK_NAME=your-stack-name
    pytest tests/integration/test_api_gateway.py -v

Note: These tests assume you're running from an allowed IP address.
"""

class TestApiGateway:

    @pytest.fixture()
    def stack_name(self):
        """ Get stack name from environment variable """
        stack_name = os.environ.get("AWS_SAM_STACK_NAME")
        if stack_name is None:
            raise ValueError('Please set the AWS_SAM_STACK_NAME environment variable to the name of your stack')
        return stack_name

    @pytest.fixture()
    def cloudformation_client(self):
        """ Get CloudFormation client """
        return boto3.client("cloudformation")

    @pytest.fixture()
    def api_gateway_client(self):
        """ Get API Gateway client """
        return boto3.client("apigateway")

    @pytest.fixture()
    def stack_outputs(self, cloudformation_client, stack_name):
        """ Get stack outputs """
        try:
            response = cloudformation_client.describe_stacks(StackName=stack_name)
        except Exception as e:
            raise Exception(
                f"Cannot find stack {stack_name} \n" f'Please make sure a stack with the name "{stack_name}" exists'
            ) from e

        stacks = response["Stacks"]
        return stacks[0]["Outputs"]

    @pytest.fixture()
    def api_gateway_url(self, stack_outputs):
        """ Get the API Gateway URL from CloudFormation Stack outputs """
        api_outputs = [output for output in stack_outputs if output["OutputKey"] == "HelloWorldApi"]

        if not api_outputs:
            raise KeyError(f"HelloWorldApi not found in stack outputs")

        return api_outputs[0]["OutputValue"]  # Extract url from stack outputs

    @pytest.fixture()
    def api_key(self, api_gateway_client, stack_outputs):
        """ Get the API Key value from API Gateway """
        # Get API Key ID from stack outputs
        api_key_outputs = [output for output in stack_outputs if output["OutputKey"] == "ApiKeyId"]

        if not api_key_outputs:
            raise KeyError(f"ApiKeyId not found in stack outputs")

        api_key_id = api_key_outputs[0]["OutputValue"]

        # Get the actual API key value
        response = api_gateway_client.get_api_key(apiKey=api_key_id, includeValue=True)
        return response["value"]

    def test_api_gateway_without_key(self, api_gateway_url):
        """ Test that API Gateway requires API key """
        response = requests.get(api_gateway_url)

        assert response.status_code == 403
        assert "message" in response.json()
        # Could be "Forbidden" or "Missing Authentication Token" depending on config

    def test_api_gateway_with_invalid_key(self, api_gateway_url):
        """ Test that API Gateway rejects invalid API key """
        headers = {"x-api-key": "invalid-key-12345"}
        response = requests.get(api_gateway_url, headers=headers)

        assert response.status_code == 403
        assert response.json() == {"message": "Forbidden"}

    def test_api_gateway_with_valid_key(self, api_gateway_url, api_key):
        """ Test that API Gateway accepts valid API key and returns correct response """
        headers = {"x-api-key": api_key}
        response = requests.get(api_gateway_url, headers=headers)

        # Should succeed
        assert response.status_code == 200

        # Check response structure
        data = response.json()
        assert "message" in data
        assert data["message"] == "hello world"
        assert "location" in data
