from django.db import models
from django.contrib.auth.hashers import make_password
from datetime import datetime, timedelta
import uuid
import jwt
import os

class User(models.Model):
    _id = models.CharField(
        primary_key = True,
        default = uuid.uuid4().hex,
        editable = False,
        max_length = 32
        )
    
    fullname = models.CharField(
        max_length = 50, 
        null = False, 
        blank = False
        )
    
    email = models.CharField(
        max_length = 100, 
        blank = False, 
        unique = True
        )
    
    username = models.CharField(
        max_length = 100, 
        blank = False, 
        unique = True
        )
    
    avatar = models.CharField(max_length=5000)
    avatar_id = models.CharField(max_length=200)

    password = models.CharField(
        max_length = 500, 
        blank = False, 
        unique = False
        )

    refreshToken = models.CharField(max_length=500)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'Users'

    def save(self, *args, **kwargs):
        print("save method is called")
        # self._id = self._id.replace('_', '')
        print("Save user into the database", self._id)
        print("Print agrs in save method: ", args)
        print("Kwagrs: ", kwargs)
        super(User, self).save(*args, **kwargs)
        
    @classmethod
    def getUserById(self, id):
        try:
            return User.objects.get(_id = id)
        except User.DoesNotExist:
            return None
    
    @classmethod        
    def getUserByUsername(self, username):
        try:
            return User.objects.get(username = username)
        except User.DoesNotExist:
            return None
    
    @classmethod
    def getUserByEmail(self, email):
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return None
        
    @classmethod
    def create_user(self, data):
        try:
            user = User.objects.create(fullname = data.get('fullname'),
                                   email = data.get('email'),
                                   username = data.get('username'),
                                   avatar = data.get('avatar'),
                                   avatar_id = data.get('avatar_id'),
                                   password = make_password(data.get('password'))
                                   )
            user.save()
            return user
        except Exception as e:
            return None
        
    def to_dict(self):
        return {
            '_id': self._id,
            'fullname': self.fullname,
            'email': self.email,
            'username': '@' + self.username,
            'avatar': self.avatar,
            # 'avatar_id': self.avatar_id,
            # 'password': self.password,
            # 'refreshToken': self.refreshToken,
            'createdAt': self.createdAt.strftime('%Y-%m-%d %H:%M:%S'),
            'updatedAt': self.updatedAt.strftime('%Y-%m-%d %H:%M:%S')
        }
        
    def generateAccessToken(self):
        print(os.getenv('ACCESS_TOKEN_EXPIRY'))
        tokenExpiry = datetime.utcnow() + timedelta(days=int(os.getenv('ACCESS_TOKEN_EXPIRY')))
        accessPayload = {
            'id': str(self._id),
            'email': self.email,
            'username': self.username,
            'exp': tokenExpiry,
            'iat': datetime.utcnow()
        }
        tokenSecretKey = os.getenv('TOKEN_SECRET')
        accessToken = jwt.encode(accessPayload, tokenSecretKey, algorithm='HS256') # generate a token
        print(type(accessToken))
        return (accessToken, tokenExpiry)
    
    def generateRefreshToken(self):
        refreshPayload = {
            'id': str(self._id),
            'exp': datetime.utcnow() + timedelta(days=int(os.getenv('REFRESH_TOKEN_EXPIRY'))),
            'iat': datetime.utcnow()
        }
        tokenSecretKey = os.getenv('TOKEN_SECRET')
        refreshToken = jwt.encode(refreshPayload, tokenSecretKey, algorithm='HS256')
        
        return refreshToken
    
    def removeFields(self, fields):
        user = {}
        for field in self._meta.fields:
            if field.name not in fields:
                user[field.name] = getattr(self, field.name)
                
        return user