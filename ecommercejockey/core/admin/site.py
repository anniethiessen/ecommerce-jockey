from django.conf import settings
from django.contrib import admin


INLINE_LIMIT = 10


admin.site.site_header = f'{settings.COMPANY_NAME} Administration'
admin.site.site_title = f'{settings.COMPANY_NAME} Admin'
admin.site.index_title = 'Home'
admin.site.site_url = settings.COMPANY_SITE
admin.site.empty_value_display = "-----"
