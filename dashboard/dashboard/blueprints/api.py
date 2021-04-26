import json
import logging
from typing import Dict

import boto3
from botocore.exceptions import ClientError
from flask import Blueprint, current_app, jsonify

blueprint = Blueprint("api", __name__, url_prefix="/api")
_logger = logging.getLogger(__name__)


def get_quicksight_embedded_dashboard_url(
    aws_account_id: str,
    aws_access_key_id: str,
    aws_secret_access_key: str,
    aws_iam_role_arn: str,
    aws_region: str,
    quicksight_dashboard_id: str,
    session_name: str,
    reset_disabled: bool = False,
    undo_redo_disabled: bool = False,
) -> Dict:
    """Generate a URL of the QuickSight dashboard that could be used to embed it into a web page.

    :param aws_account_id: AWS account ID
    :type aws_account_id: str

    :param aws_access_key_id: AWS API access key
    :type aws_access_key_id: str

    :param aws_secret_access_key: AWS API secret key
    :type aws_secret_access_key: str

    :param aws_iam_role_arn: ARN of the AIM role allowing to embed QuickSight dashboards
    :type aws_iam_role_arn: str

    :param aws_region: AWS region
    :type aws_region: str

    :param quicksight_dashboard_id: QuickSight dashboard's ID
    :type quicksight_dashboard_id: str

    :param session_name: Session name - must be equal to the QuickSight user's email
    :type session_name: str

    :param reset_disabled: Boolean value indicating whether Disable Reset button is available in the embedded dashboard
    :type reset_disabled: bool

    :param undo_redo_disabled: Boolean value indicating whether
        Disable Undo/Redo buttons are available in the embedded dashboard
    :type undo_redo_disabled: bool

    :return: Python dictionary containing the URL of the QuickSight dashboard
        that could be used to embed it to a web page along with the metadata
    :rtype: Dict
    """
    try:
        sts_client = boto3.client(
            "sts",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )

        assumed_aim_role = sts_client.assume_role(
            RoleArn=aws_iam_role_arn,
            RoleSessionName=session_name,
        )
    except ClientError:
        _logger.exception(
            f"An unexpected exception occurred while trying to assume role {aws_iam_role_arn}"
        )
        raise
    else:
        assumed_aim_role_session = boto3.Session(
            aws_access_key_id=assumed_aim_role["Credentials"]["AccessKeyId"],
            aws_secret_access_key=assumed_aim_role["Credentials"]["SecretAccessKey"],
            aws_session_token=assumed_aim_role["Credentials"]["SessionToken"],
        )
        try:
            quicksight_client = assumed_aim_role_session.client(
                "quicksight", region_name=aws_region
            )

            response = quicksight_client.get_dashboard_embed_url(
                AwsAccountId=aws_account_id,
                DashboardId=quicksight_dashboard_id,
                IdentityType="IAM",
                SessionLifetimeInMinutes=600,
                UndoRedoDisabled=undo_redo_disabled,
                ResetDisabled=reset_disabled,
            )

            return {
                "statusCode": 200,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type",
                },
                "body": json.dumps(response),
                "isBase64Encoded": bool("false"),
            }
        except ClientError:
            _logger.exception(
                "An unexpected error occurred while trying to generate an embedded URL"
            )
            raise


@blueprint.route("/dashboard_url", methods=("GET",))
def dashboard_url():
    result = get_quicksight_embedded_dashboard_url(
        aws_account_id=current_app.config["AWS_ACCOUNT_ID"],
        aws_access_key_id=current_app.config["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=current_app.config["AWS_SECRET_ACCESS_KEY"],
        aws_iam_role_arn=current_app.config["AWS_IAM_ROLE"],
        aws_region=current_app.config["AWS_REGION"],
        quicksight_dashboard_id=current_app.config["QUICKSIGHT_DASHBOARD_ID"],
        session_name=current_app.config["QUICKSIGHT_USER_EMAIL"],
    )

    return jsonify(result)
