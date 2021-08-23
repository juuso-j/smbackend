from services.models.unit_count import BaseUnitCount
import sys, inspect
from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

#from .models import Service, UnitServiceDetails
from services.models import * 
from services.models.notification import Announcement, ErrorMessage, Notification

class NotificationAdmin(TranslationAdmin):
    list_display = ("title", "active", "content")
    list_display_links = ("title", "content")
    list_filter = ("active",)


class ServiceNodeAdmin(admin.ModelAdmin):
    search_fields = ("id", "name")

class UnitAdmin(admin.ModelAdmin):
    search_fields = ["id", "name"]

admin.site.register(Announcement, NotificationAdmin)
admin.site.register(ErrorMessage, NotificationAdmin)
admin.site.register(Service)
admin.site.register(UnitServiceDetails)
admin.site.register(AccessibilityVariable)
admin.site.register(Department)
admin.site.register(Keyword)
#admin.site.register(Notification)
admin.site.register(ServiceMapping)
admin.site.register(ServiceNode, ServiceNodeAdmin)
admin.site.register(UnitAccessibilityProperty)
admin.site.register(UnitAccessibilityShortcomings)
admin.site.register(UnitAlias)
admin.site.register(UnitConnection)
#admin.site.register(BaseUnitCount)
admin.site.register(ServiceNodeUnitCount)
admin.site.register(ServiceUnitCount)
admin.site.register(UnitEntrance)
admin.site.register(UnitIdentifier)
admin.site.register(Unit, UnitAdmin)
