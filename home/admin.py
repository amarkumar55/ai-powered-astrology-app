from django.contrib import admin
from .models import ContactQuery


@admin.register(ContactQuery)
class ContactAdminModel(admin.ModelAdmin):
    list_display = ('full_name','email', 'message', 'created_at','updated_at')
    sortable_by = ('updated_at')
    search_fields = ('email', 'full_name','created_at')
    list_filter = ('created_at', 'updated_at')
