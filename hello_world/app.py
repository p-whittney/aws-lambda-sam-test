import json
import time
import os
import requests

try:
    from opentelemetry import trace
    tracer = trace.get_tracer(__name__)
    TRACING_ENABLED = True
except Exception as e:
    print(f"OpenTelemetry not available: {e}")
    TRACING_ENABLED = False
    
    # Create a no-op tracer for local development
    class NoOpSpan:
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
    
    class NoOpTracer:
        def start_as_current_span(self, name):
            return NoOpSpan()
    
    tracer = NoOpTracer()


def lambda_handler(event, context):
    """Sample pure Lambda function with OpenTelemetry tracing

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """

    # Create a custom span to trace specific work
    with tracer.start_as_current_span("process_request"):
        is_local = os.environ.get('AWS_SAM_LOCAL') == 'true'
        print(f"Processing request (tracing={'disabled' if is_local else 'enabled'}, local={is_local})")
        
        # Fetch external IP
        with tracer.start_as_current_span("fetch_ip"):
            try:
                ip = requests.get("http://checkip.amazonaws.com/", timeout=5)
                location = ip.text.replace("\n", "")
            except requests.RequestException as e:
                print(f"Error fetching IP: {e}")
                location = "unknown"
        
        # Simulate some processing
        with tracer.start_as_current_span("process_data"):
            time.sleep(0.1)  # Simulate work
            message = "hello world"
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": message,
                "location": location,
                "version": "v1.1"
            }),
        }
