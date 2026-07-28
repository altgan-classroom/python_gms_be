"""Custom HTTPException classes that extend werkzeug.exceptions."""
from werkzeug.exceptions import Unauthorized, Forbidden

_realm = "registered_user@gymowners.com"


class ApiUnauthorized(Unauthorized):
    def __init__(self, description="Unauthorized", error=None, error_description=None, ):
        self.description = description
        self.www_auth_value = self.__get_www_auth_value(error, error_description)
        Unauthorized.__init__(self, description=description, response=None, www_authenticate=None)

    def get_headers(self, environ, scope=None):
        return [("Content-Type", "text/html"), ("WWW-Authenticate", self.www_auth_value)]

    def __get_www_auth_value(self, error, error_description):
        www_auth_value = f'Bearer realm="{_realm}"'
        if error:
            www_auth_value += f', error="{error}"'
        if error_description:
            www_auth_value += f', error_description="{error_description}"'
        return www_auth_value


class ApiForbidden(Forbidden):
    def get_headers(self, environ, scope=None):
        return [
            ("Content-Type", "text/html"),
            (
                "WWW-Authenticate",
                f'Bearer realm="{_realm}", '
                'error="insufficient_scope", '
                'error_description="You don''t have access to this API"',
            ),
        ]


class DoorAccessException(Exception):
    def __init__(self, user_id=None, resource_id=None, url=None, data=None, response=None, message=None):
        super().__init__(message)
        self.url = url
        self.data = data
        self.response = response
        self.message = message
        self.user_id = user_id
        self.resource_id = resource_id


class UploadDocumentError(Exception):
    pass


class FileFormatError(Exception):
    pass


class FileSizeError(Exception):
    pass


class TimeConversionError(Exception):
    pass
