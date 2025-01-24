
def apiError(code, message="Something Wrong"):
    return {
        'status_code': code,
        'message': message,
        'success': False
    }
    
