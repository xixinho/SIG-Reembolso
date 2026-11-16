"""Ponto de entrada WSGI (usa as configuracoes de producao por padrao)."""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sig_reembolso.settings.prod")

application = get_wsgi_application()