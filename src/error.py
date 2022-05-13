'''error file'''
from werkzeug.exceptions import HTTPException

class AccessError(HTTPException):
    """definition of accesserror"""
    code = 400
    message = 'No message specified'

class InputError(HTTPException):
    """definition of inputerror"""
    code = 400
    message = 'No message specified'
