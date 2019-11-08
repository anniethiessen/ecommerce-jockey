from rest_framework.generics import CreateAPIView

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from .decorators import webhook
from .serializers import ProductOrderCreateSerializer


class ProductOrderCreateView(CreateAPIView):
    serializer_class = ProductOrderCreateSerializer

    @method_decorator(csrf_exempt)
    @method_decorator(webhook)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def perform_create(self, serializer):
        print('hey')
        return super().perform_create(serializer)
