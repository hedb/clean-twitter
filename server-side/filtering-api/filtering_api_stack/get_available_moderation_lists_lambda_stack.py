import os
import shutil
import aws_cdk as cdk
from constructs import Construct
from aws_cdk import (aws_apigateway as apigateway,
                     aws_dynamodb as dynamodb,
                     aws_lambda as lambda_)


def package_layer():
    # Step 1: Verify we have a directory packaging_temp
    if not os.path.exists("packaging_temp"):
        os.makedirs("packaging_temp")

    # Step 2: Run pip install -r layer_requirements.txt into packaging_temp
    os.system("pip install -r requirements_lambda_layer.txt -t packaging_temp")

    # Step 3: Remove layer_deployment if it exists
    if os.path.exists("layer_deployment"):
        shutil.rmtree("layer_deployment")

    # Step 4: Create layer_deployment
    os.makedirs("layer_deployment/python")

    # Step 5: Copy packaging_temp content directly into layer_deployment
    for item in os.listdir("packaging_temp"):
        s = os.path.join("packaging_temp", item)
        d = os.path.join("layer_deployment/python", item)
        if os.path.isdir(s):
            shutil.copytree(s, d)
        else:
            shutil.copy2(s, d)

    # Step 6: Copy layer_common_src into layer_deployment
    shutil.copytree("common_src", os.path.join("layer_deployment/python", "common_src"))


class GetAvailableModerationListsService(Construct):
    def __init__(self, scope: Construct, id: str):
        super().__init__(scope, id)

        dynamoDB_table = dynamodb.Table(self, "get-available-moderation-lists",
                                        partition_key=dynamodb.Attribute(name="primaryID",
                                                                         type=dynamodb.AttributeType.STRING),
                                        table_name="moderation-lists",
                                        removal_policy=cdk.RemovalPolicy.RETAIN
                                        )

        package_layer()

        common_layer = lambda_.LayerVersion(self, "CommonLayer",
                                            code=lambda_.Code.from_asset("layer_deployment"),
                                            compatible_runtimes=[lambda_.Runtime.PYTHON_3_11],
                                            description="Common utilities for Lambda functions"
                                            )

        handler = lambda_.Function(self, "get-available-moderation-lists-lambda",
                    runtime=lambda_.Runtime.PYTHON_3_11,
                    code=lambda_.Code.from_asset("get_available_moderation_lists_lambda"),
                    handler="lambda.main_handler"
                    ,environment=dict( TABLE_NAME=dynamoDB_table.table_name)
                    ,layers=[common_layer]
        )

        dynamoDB_table.grant_read_data(handler)

        api = apigateway.RestApi(self, "get-available-moderation-list-api",
                  rest_api_name="get-available-moderation-lists_name",
                  description="get-available-moderation-lists_description")

        get_available_moderation_lists_lambda_integration = apigateway.LambdaIntegration(handler,
                request_templates={"application/json": '{ "statusCode": "200" }'})

        api.root.add_method("GET", get_available_moderation_lists_lambda_integration)   # GET /

# if __name__ == '__main__':
#     package_layer()