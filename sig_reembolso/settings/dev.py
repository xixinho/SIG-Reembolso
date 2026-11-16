"""Desenvolvimento local."""
from .base import *  # noqa: F401,F403

DEBUG = True

# Chave valida somente para desenvolvimento. Em producao ela vem do ambiente.
SECRET_KEY = SECRET_KEY or "django-insecure-somente-desenvolvimento"  # noqa: F405

ALLOWED_HOSTS = []