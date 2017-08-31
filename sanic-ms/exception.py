#!/usr/bin/env python
# -*- coding: utf-8 -*-



class CustomException(Exception):
    status_code = None
    code = 100001
    message = None
    error = None
    def __init__(self, error=None, code=None, message=None, status_code=None):
        super().__init__(message)
        if message:
            self.message = message
        if code:
            self.code = code
        if status_code:
            self.status_code = status_code
        self.error = error

class BadRequest(CustomException):
    status_code = 400
    message = "Bad Request"

class Unauthorized(CustomException):
    status_code = 401
    message = "Unauthorized"

class Forbidden(CustomException):
    status_code = 403
    message = "Not Found"

class NotFound(CustomException):
    status_code = 404
    message = "Not Found"

class NotAcceptable(CustomException):
    status_code = 406
    message = "Unauthorized"

class Gone(CustomException):
    status_code = 410
    message = "Unauthorized"

class Enhance(CustomException):
    status_code = 420
    message = "Enhance Your Calm"

class UnprocessableEntity(CustomException):
    status_code = 422
    message = "Unprocessable Entity"

class TooManyRequests(CustomException):
    status_code = 429
    message = "Too Many Requests"

class ServerError(CustomException):
    status_code = 500
    message = "Internal Server Error"

class BadGateway(CustomException):
    status_code = 502
    message = "Bad Gateway"

class ServiceUnavailable(CustomException):
    status_code = 503
    message = "Service Unavailable"

class GatewayTimeout(CustomException):
    status_code = 504
    message = "Gatewa timeout"
