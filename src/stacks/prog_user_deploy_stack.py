from aws_cdk import (
    # Duration,
    Stack,
    # aws_sqs as sqs,
)
from constructs import Construct
from ..constructs.iam_role import IAMSetup
class Cdkv2ProgUserDeployStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, props: dict, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        IAMSetup(self, "DemoUser", props= props)