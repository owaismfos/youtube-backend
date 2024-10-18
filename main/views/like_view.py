from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from main.models.like_model import Like
from main.utils.api_response import apiResponse
from main.utils.api_error import apiError

class LikeView(APIView):
    def get(self, request, videoId):
        likesCount = Like.likesCountOfVideo(videoId)
        isLiked = Like.isLikedVideo(request.user.id, videoId)

        data = {
            'likesCount': likesCount,
            'isLiked': isLiked
        }
        return Response(apiResponse(200, "OK", data), status=200)

    def post(self, request, videoId):
        like = Like.likeVideo(request.user.id, videoId)
        return Response(apiResponse(200, "OK", like), status=200)


class UnlikeView(APIView):
    def post(self, request, videoId):
        unlikeVideo = Like.unlikeVideo(request.user.id, videoId)
        return Response(apiResponse(200, "Unlike the video"), status=200)