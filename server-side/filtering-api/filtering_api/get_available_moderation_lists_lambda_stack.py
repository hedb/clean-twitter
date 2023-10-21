import aws_cdk as cdk
from constructs import Construct
from aws_cdk import (aws_apigateway as apigateway,
                     aws_s3 as s3,
                     aws_lambda as lambda_)

class GetAvailableModerationListsService(Construct):
    def __init__(self, scope: Construct, id: str):
        super().__init__(scope, id)

        # bucket = s3.Bucket(self, "WidgetStore")

        handler = lambda_.Function(self, "get-available-moderation-lists-lambda",
                    runtime=lambda_.Runtime.PYTHON_3_11,
                    code=lambda_.Code.from_asset("get_available_moderation_lists_lambda"),
                    handler="lambda.main_handler"
                    # ,environment=dict( BUCKET=bucket.bucket_name)
                    )

        # bucket.grant_read_write(handler)

        api = apigateway.RestApi(self, "get-available-moderation-list-api",
                  rest_api_name="get-available-moderation-lists_name",
                  description="get-available-moderation-lists_description")

        get_available_moderation_lists_lambda_integration = apigateway.LambdaIntegration(handler,
                request_templates={"application/json": '{ "statusCode": "200" }'})

        api.root.add_method("GET", get_available_moderation_lists_lambda_integration)   # GET /