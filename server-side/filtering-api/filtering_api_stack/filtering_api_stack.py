import subprocess
from aws_cdk import (
    # Duration,
    Stack,
    # aws_sqs as sqs,
)
from constructs import Construct
from . import get_available_moderation_lists_lambda_stack
from . import crosscheck_userids_vs_lists_lambda_stack
from . import common_lambda_layer_stack

class FilteringApiStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        result = subprocess.run(["flake8", "common_src/", "crosscheck_userids_vs_lists_lambda", "get_available_moderation_lists_lambda"], capture_output=True,
                                text=True)

        if result.returncode != 0:
            print("Linting errors detected:")
            print(result.stdout)
            raise Exception("Linter failed. Deployment halted.")

        common_layer = common_lambda_layer_stack.CommonLambdaLayer(self, "common-lambda-layer")

        get_available_moderation_lists_lambda_stack.GetAvailableModerationListsService(
            self, "get-available-moderation-lists",common_layer.layer_version)

        crosscheck_userids_vs_lists_lambda_stack.CrosscheckUserids_VS_ListsService(
        self, "crosscheck-userids-vs-lists",common_layer.layer_version)