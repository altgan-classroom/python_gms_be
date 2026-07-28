from http import HTTPStatus
import boto3
from auth_admin_service.admin.dtos.admin_requests import Path, UserPath, LocationPath
from auth_admin_service.auth.dtos.auth_requests import UploadRequest
from gmsshared.src.config import get_config
from gmsshared.src.models.location import Location
from gmsshared.src.models.user import User
from gmsshared.src.util.enums import ResponseStatusEnum
from gmsshared.src.util.misc import create_response


def get_presigned_url(path: Path, query: UploadRequest):

    s3_client = boto3.client('s3', aws_access_key_id=get_config().UPLOAD_S3_KEY,
                             aws_secret_access_key=get_config().UPLOAD_S3_SECRET,
                             region_name='us-east-1')

    if isinstance(path, UserPath):
        user_id = path.user_id
    elif isinstance(path, LocationPath):
        location_id = path.location_id
    if query.type == 'logo':
        key = f"{query.type}/{location_id}_location_{query.name}"
    else:
        key = f"{query.type}/{user_id}_user_{query.name}"

    response = s3_client.generate_presigned_post(Bucket=get_config().UPLOAD_S3_BUCKET,
                                                 Key=key,
                                                 ExpiresIn=int(get_config().UPLOAD_URL_EXPIRE),
                                                 Fields={"acl": "public_read"},
                                                 Conditions=[["content-length-range", 0,
                                                              get_config().UPLOAD_SIZE_LIMIT]])
    response['final_url'] = f"https://{get_config().UPLOAD_S3_BUCKET}/{key}"
    return create_response(status_code=HTTPStatus.OK, status=ResponseStatusEnum.CREATED, logger_name=__name__,
                           data=response, message="Created presigned url")