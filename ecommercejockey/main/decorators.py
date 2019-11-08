import json
from functools import wraps

from django.conf import settings
from django.http import (
    HttpResponseBadRequest,
    HttpResponseForbidden
)

from core.utils import hmac_is_valid


def webhook(f):
    """
    A view decorator that checks and validates a Shopify Webhook
    request.

    """

    @wraps(f)
    def wrapper(request, *args, **kwargs):
        try:
            topic = request.META['HTTP_X_SHOPIFY_TOPIC']
            domain = request.META['HTTP_X_SHOPIFY_SHOP_DOMAIN']
            data = json.loads(request.body.decode('utf-8'))
            hmac = request.META.get('HTTP_X_SHOPIFY_HMAC_SHA256')
            body = request.body
        except (KeyError, ValueError) as e:
            return HttpResponseBadRequest()

        if not domain == f'{settings.SHOPIFY_SHOP_NAME}.myshopify.com':
            return HttpResponseBadRequest()

        if not hmac_is_valid(body, settings.SHOPIFY_WEBHOOK_SIGNATURE, hmac):
            return HttpResponseForbidden()

        request.webhook_topic = topic
        request.webhook_data = data
        request.webhook_domain = domain
        return f(request, *args, **kwargs)

    return wrapper
