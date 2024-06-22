from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status

from main.models.comment_model import Comment
from main.utils.api_response import apiResponse
from main.utils.api_error import apiError


class CommentView(APIView):
    def get(self, request, videoId):
        comments = Comment.comments(videoId)
        return Response(apiResponse(200, 'comment retrieved successfully', comments), status=200)
    
    def post(self, request, videoId):
        comment = Comment.commentOnVideo(request.user._id, videoId, request.data.get('comment'))
        
        return Response(apiResponse(200, 'comment created successfully', comment), status=200)