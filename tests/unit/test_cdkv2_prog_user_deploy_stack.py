import aws_cdk as core
import aws_cdk.assertions as assertions

from src.stacks.prog_user_deploy_stack import Cdkv2ProgUserDeployStack

# example tests. To run these tests, uncomment this file along with the example
# resource in src/cdkv2_prog_user_deploy_stack.py
def test_prog_user():
    app = core.App()
    stack = Cdkv2ProgUserDeployStack(app, "cdkv2-prog-user-deploy")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
