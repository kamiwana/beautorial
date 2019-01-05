from rest_framework.generics import ListAPIView
from .serializers import *
from rest_framework.response import Response

# Create your views here.
class ProductList(ListAPIView):

    serializer_class = ProductSerializer

    def list(self, *args, **kwargs):
        queryset = Product.objects.filter(is_view=1)
        serializer = self.get_serializer(queryset, many=True)

        return Response({
            "result": 1,
            "data": serializer.data
        })