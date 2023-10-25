from aws_cdk import (
    # Duration,
    Stack,
    # aws_sqs as sqs,
)
from constructs import Construct
from . import get_available_moderation_lists_lambda_stack
from . import crosscheck_userids_vs_lists_lambda_stack

class FilteringApiStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        get_available_moderation_lists_lambda_stack.GetAvailableModerationListsService(self, "get-available-moderation-lists")

        # crosscheck_userids_vs_lists_lambda_stack.CrosscheckUserids_VS_ListsService(self, "crosscheck-userids-vs-lists")