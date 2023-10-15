#!/usr/bin/env python3
import os

import aws_cdk as cdk
from aws_cdk import Aspects
from cdk_nag import AwsSolutionsChecks, NagSuppressions

from src.stacks.prog_user_deploy_stack import Cdkv2ProgUserDeployStack

from project_configs.helpers.project_configs import props, env_devsecops_account
from project_configs.helpers.helper import set_tags

app = cdk.App()
stack = Cdkv2ProgUserDeployStack(app, "Cdkv2ProgUserDeployStack",
                                 stack_name="Cdkv2ProgUserDeployStack",
                                 props=props,
                                 env=env_devsecops_account

                                 )
Aspects.of(app).add(AwsSolutionsChecks(verbose=True))
NagSuppressions.add_stack_suppressions(stack=stack, suppressions=[{
    "id": "AwsSolutions-SMG4", "reason": "Is not necessary, is a user Key"},
    {"id": "AwsSolutions-IAM5", "reason": "Exception ECR auth"},
])
set_tags(stack=stack, tags=props["tags"])
app.synth()
