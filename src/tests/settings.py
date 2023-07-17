import os
from settings.common import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'dynamic-table-test.db'),
    }
}

DEBUG = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'default': {
            'format': '[%(asctime)s %(levelname)s/%(processName)s/%(threadName)s] [%(name)s(%(funcName)s)(%(lineno)d)] %(message)s',
            'datefmt': "%Y-%b-%d %H:%M:%S"
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'DEBUG'
        },
    }
}
