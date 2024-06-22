
def apiResponse(code, message="success", data = None):
    return {
        'status_code': code,
        'message': message,
        'data': data,
        'success': True
    }