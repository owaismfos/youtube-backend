
def apiError(code, message="Somthing wrong"):
    return {
        'status_code': code,
        'message': message,
        'success': False
    }
    
