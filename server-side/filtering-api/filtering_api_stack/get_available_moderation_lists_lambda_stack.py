import aws_cdk as cdk
from constructs import Construct
from aws_cdk import (aws_apigateway as apigateway,
                     aws_dynamodb as dynamodb,
                     aws_lambda as lambda_)
from common_src import moderation_lists_util



class GetAvailableModerationListsService(Construct):
    def __init__(self, scope: Construct, id: str, common_layer:lambda_.LayerVersion):
        super().__init__(scope, id)

        dynamoDB_table = dynamodb.Table(self, "get-available-moderation-lists",
                                        partition_key=dynamodb.Attribute(name="primaryID",
                                                                         type=dynamodb.AttributeType.STRING),
                                        table_name=moderation_lists_util.TABLE_NAME,
                                        removal_policy=cdk.RemovalPolicy.RETAIN
                                        )

        handler = lambda_.Function(self, "get-available-moderation-lists-lambda",
                    runtime=lambda_.Runtime.PYTHON_3_11,
                    code=lambda_.Code.from_asset("get_available_moderation_lists_lambda"),
                    handler="lambda.main_handler"
                    ,layers=[common_layer]
        )

        dynamoDB_table.grant_read_data(handler)

        api = apigateway.RestApi(self, "get-available-moderation-list-api",
                  rest_api_name="get-available-moderation-lists_name",
                  description="get-available-moderation-lists_description")

        get_available_moderation_lists_lambda_integration = apigateway.LambdaIntegration(handler,
                request_templates={"application/json": '{ "statusCode": "200" }'})

        api.root.add_method("GET", get_available_moderation_lists_lambda_integration)   # GET /
