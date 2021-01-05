from django.contrib import admin
from .models import ArkStock, ArkFund
from django.contrib.auth.models import User, Group

# Register your models here.
admin.site.unregister(Group)
admin.site.unregister(User)


class ArkStockAdmin(admin.ModelAdmin):
    list_display = ['__str__']
    search_fields = ['company']
    list_filter = ('fund',)


class ArkFundAdmin(admin.ModelAdmin):
    list_display = ['ticker', 'update_now']
    list_editable = ['update_now']


admin.site.register(ArkFund, ArkFundAdmin)
admin.site.register(ArkStock, ArkStockAdmin)
