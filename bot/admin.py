from django.contrib import admin
from .models import ArkStock,ArkFund
from django.contrib.auth.models import User, Group

# Register your models here.
admin.site.unregister(Group)
admin.site.unregister(User)



class ArkStockAdmin(admin.ModelAdmin):
    list_display = ['__str__']
    search_fields = ['company']
    list_filter = ('fund',)

admin.site.register(ArkFund)
admin.site.register(ArkStock, ArkStockAdmin)
