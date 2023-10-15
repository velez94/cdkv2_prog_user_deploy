from aws_cdk import (
    Aws,
    aws_iam as iam,
    aws_secretsmanager as secretsmanager,
    CfnOutput

)
from constructs import Construct


class IAMSetup(Construct):

    def __init__(self, scope: Construct, construct_id: str, props: dict, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        # Getting props
        project_name = props.get("project_name", "demo")
        roles = props.get("iam_properties", {}).get("assume_roles", [])
        user_name = props.get("iam_properties", {}).get("user_name", f"{project_name}_user")
        context = props.get("iam_properties", {}).get("context", {"from": "2023-01-01T00:00:00Z",
                                                                  "up": "2023-06-30T23:59:59Z"})
        ecr_repositories = props.get("ecr_repositories", False)

        rs = []
        if roles:
            for r in roles:
                rs.append(r["arn"])
        else:
            rs = [f"arn:aws:iam::{Aws.ACCOUNT_ID}:role/cdk-hnb659fds-cfn-exec-role-{Aws.ACCOUNT_ID}-{Aws.REGION}"]
        # Creating statement
        st = iam.PolicyStatement(actions=["sts:AssumeRole"], effect=iam.Effect.ALLOW, resources=rs)


        ext_id = secretsmanager.Secret(self, "IDSecret", secret_name=f"/{project_name}/SecretExternalID",
                                       generate_secret_string=secretsmanager.SecretStringGenerator(
                                           secret_string_template='{"type": "role_ext_id"}',
                                           exclude_punctuation=True,
                                           exclude_characters="-`",

                                           generate_string_key='external_id'
                                       )
                                       )
        self.role = iam.Role(self, "CustomRole", role_name=f"Role{project_name.capitalize()}",
                             assumed_by=iam.PrincipalWithConditions(iam.AccountPrincipal(account_id=Aws.ACCOUNT_ID),

                                                                    conditions={
                                                                        "StringLike": {
                                                                            "sts:RoleSessionName": "${aws:username}"
                                                                        },
                                                                        "DateGreaterThan": {
                                                                            "aws:CurrentTime": context["from"]},
                                                                        "DateLessThan": {
                                                                            "aws:CurrentTime": context["up"]}
                                                                    }
                                                                    ),

                             # Using a SecretValue here risks exposing your secret.
                             #  Call AWS Secrets Manager directly in your runtime code. Call 'secretValue.unsafeUnwrap()' if you understand and accept the risks.
                             external_ids=[ext_id.secret_value_from_json('external_id').unsafe_unwrap()]
                             )

        self.role.add_to_policy(st)
        self.role.node.add_dependency(ext_id)

        # Creating  iam programmatic user

        self.user = iam.User(self, user_name, user_name=user_name, path=f"/{project_name}/")
        # Create Access key and secret key for user
        access_key = iam.AccessKey(self, "AccessKey", user=self.user)

        secretsmanager.Secret(self, "Secret",
                              secret_name=f"/{project_name}/UserAccessKey",
                              secret_string_value=access_key.secret_access_key
                              )
        # Create Group
        self.group = iam.Group(self, f"Group_{project_name}", group_name=f"{project_name}Group")
        self.user.add_to_group(self.group)

        # Grant User assume role
        self.role.grant_assume_role(self.group)

        # Add additional permissions for ecr
        if ecr_repositories:
            rsc= []
            for e in ecr_repositories:
                rsc.append(f"arn:aws:ecr:{e['region']}:{e['account']}:repository/{e['name']}")
            st_ecr = iam.PolicyStatement(actions=[
                "ecr:BatchCheckLayerAvailability",
                "ecr:GetDownloadUrlForLayer",
                "ecr:GetRepositoryPolicy",
                "ecr:DescribeRepositories",
                "ecr:ListImages",
                "ecr:DescribeImages",
                "ecr:BatchGetImage",
                "ecr:InitiateLayerUpload",
                "ecr:UploadLayerPart",
                "ecr:CompleteLayerUpload",
                "ecr:PutImage"],
                effect=iam.Effect.ALLOW,
                resources=rsc)
            st_auth_ecr = iam.PolicyStatement(actions=["ecr:GetAuthorizationToken"],
                                              effect=iam.Effect.ALLOW,
                                              resources=["*"]
                                          )
            self.role.add_to_policy(st_ecr)
            self.role.add_to_policy(st_auth_ecr)
            # Audit user Activity
        CfnOutput(self, "RoleARN", value=self.role.role_arn, description=f"Role ARN ")
