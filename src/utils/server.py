#pylint: disable=C0103, C0301
"""
Utilities for the server
"""
__author__ = "Noupin"

#Third Party Imports
import functools

def checkToken(f):
    """
    Checks the validity and expiration of the JWT
    """

    @functools.wraps(f)
    def decorated(*args, **kwargs):
        authorization = flask.request.headers['Authorization'].split(' ')

        if len(authorization) <= 1:
            return {'message': 'Token missing.'}, 403

        token = authorization[1]

        if len(token) == 0:
            return {'message': 'Token empty.'}, 403
        
        try: 
            data = jwt.decode(token, public_key, algorithms="RS256")
        except jwt.ExpiredSignatureError:
            return {'message': 'Token has timed out.'}, 403
        except:
            return {'message': 'Signature invalid.'}, 403

        return f(*args, **kwargs)

    return decorated