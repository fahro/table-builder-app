from django.urls import path, include

api_urls = [
    path('table/', include('dynamic_table.api.core.urls')),
]
