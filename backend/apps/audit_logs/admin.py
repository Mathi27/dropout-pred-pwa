from django.contrib import admin

from apps.audit_logs.models import AuditLog

admin.site.register(AuditLog)
