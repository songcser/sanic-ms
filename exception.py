#!/usr/bin/env python
# -*- coding: utf-8 -*-



class BaseException(Exception):
    status_code = None
    code = 100001
    message = None
    error = None
    def __init__(self, message=None, code=None, status_code=None, error=None):
        super().__init__(message)
        if message:
            self.message = message
        if code:
            self.code = code
        if status_code:
            self.status_code = status_code
        self.error = error

class BadRequest(BaseException):
    status_code = 400
    message = "Bad Request"

class Unauthorized(BaseException):
    status_code = 401
    message = "Unauthorized"

class Forbidden(BaseException):
    status_code = 403
    message = "Not Found"

class NotFound(BaseException):
    status_code = 404
    message = "Not Found"

class NotAcceptable(BaseException):
    status_code = 406
    message = "Unauthorized"

class Gone(BaseException):
    status_code = 410
    message = "Unauthorized"

class Enhance(BaseException):
    status_code = 420
    message = "Enhance Your Calm"

class UnprocessableEntity(BaseException):
    status_code = 422
    message = "Unprocessable Entity"

class TooManyRequests(BaseException):
    status_code = 429
    message = "Too Many Requests"

class ServerError(BaseException):
    status_code = 500
    message = "Internal Server Error"

class BadGateway(BaseException):
    status_code = 502
    message = "Bad Gateway"

class ServiceUnavailable(BaseException):
    status_code = 503
    message = "Service Unavailable"

class GatewayTimeout(BaseException):
    status_code = 504
    message = "Gatewa timeout"
