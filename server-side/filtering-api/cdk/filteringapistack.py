from aws_cdk import core
from aws_cdk.aws_lambda import Function, Code, Runtime
from aws_cdk.aws_apigateway import RestApi, LambdaIntegration

class FilteringAPIStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Define the Lambda function
        hello_lambda = Function(self, "HelloLambda",
            runtime=Runtime.PYTHON_3_8,
            handler="app.handler",
            code=Code.from_asset("lambda"),
        )

        # Define the API Gateway
        hello_api = RestApi(self, "HelloApi")
        hello = hello_api.root.add_resource("hello")
        hello.add_method("GET", LambdaIntegration(hello_lambda))
