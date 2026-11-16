"""Producao: SECRET_KEY e ALLOWED_HOSTS obrigatorios no ambiente."""
import os

from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F401,F403

DEBUG = False

if not SECRET_KEY:  # noqa: F405
    raise ImproperlyConfigured("Defina a variavel de ambiente SECRET_KEY.")

ALLOWED_HOSTS = [h for h in os.environ.get("ALLOWED_HOSTS", "").split(",") if h]