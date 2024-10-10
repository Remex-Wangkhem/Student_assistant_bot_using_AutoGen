from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import PostSerializer
from ..models import Post

@api_view(['GET'])
def post_list(request):
    posts = Post.objects.all()
    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data)
