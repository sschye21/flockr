'''echo sample'''
from error import InputError
def echo(value):
    """echo definition"""
    if value == 'echo':
        raise InputError(description='Input cannot be echo')
    return value
