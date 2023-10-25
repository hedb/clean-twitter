import aws_cdk as cdk
from constructs import Construct
from aws_cdk import (aws_apigateway as apigateway,
                    aws_dynamodb as dynamodb,
                    aws_lambda as lambda_)
from common_src import moderation_lists_util

class CrosscheckUserids_VS_ListsService(Construct):
    def __init__(self, scope: Construct, id: str,common_layer:lambda_.LayerVersion):
        super().__init__(scope, id)

        dynamoDB_table = dynamodb.Table(self, "moderation-lists-users-mapping",
                    partition_key=dynamodb.Attribute(name="user_id", type=dynamodb.AttributeType.STRING),
                    sort_key=dynamodb.Attribute(name="list_id", type=dynamodb.AttributeType.STRING),
                    table_name="moderation-lists-users-mapping",
                    removal_policy=cdk.RemovalPolicy.DESTROY
        )

        handler = lambda_.Function(self, "crosscheck-userids-vs-lists-lambda",
                    runtime=lambda_.Runtime.PYTHON_3_11,
                    code=lambda_.Code.from_asset("crosscheck_userids_vs_lists_lambda"),
                    handler="lambda.main_handler"
                    ,environment=dict( TABLE_NAME=dynamoDB_table.table_name)
                    ,layers=[common_layer]
        )

        dynamoDB_table.grant_read_data(handler)

        moderation_list_table = dynamodb.Table.from_table_name(self, "moderation-lists",
                                                               moderation_lists_util.TABLE_NAME)
        moderation_list_table.grant_read_data(handler)


        api = apigateway.RestApi(self, "crosscheck-userids-vs-lists-api",
                  rest_api_name="crosscheck-userids-vs-lists_name",
                  description="crosscheck-userids-vs-lists_description")

        crosscheck_userids_vs_lists_lambda_integration = apigateway.LambdaIntegration(handler,
                request_templates={"application/json": '{ "statusCode": "200" }'})

        api.root.add_method("post", crosscheck_userids_vs_lists_lambda_integration) 