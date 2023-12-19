from .base import *
from django.contrib.messages import constants as messages
SECRET_KEY = 'django-insecure-f&s_o5=zm_fjndxzwo1xsm5e5%9w1h51x35l_2(g7me)e-)i_!'


DEBUG = True

ALLOWED_HOSTS = ['*']
MESSAGE_TAGS = {
messages.DEBUG: 'alert-info',
messages.INFO: 'alert-info',
messages.SUCCESS: 'alert-success',
messages.WARNING: 'alert-warning',
messages.ERROR: 'alert-danger',
}

EMAIL_HOST = 'sandbox.smtp.mailtrap.io'
EMAIL_HOST_USER = '61107b2271529b'
EMAIL_HOST_PASSWORD = '73a8ada41340ee'
EMAIL_PORT = '2525'