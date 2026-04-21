import os
from datetime import timedelta

SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

SESSION_TYPE = 'filesystem'
SESSION_PERMANENT = False
PERMANENT_SESSION_LIFETIME = timedelta(hours=1)
