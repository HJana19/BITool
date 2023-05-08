from django.contrib import admin
from .models import Employee,ImpactActions,SovrnTransactions,CJTransactions


class EmployeeAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Employee._meta.fields]


admin.site.register(Employee, EmployeeAdmin)


@admin.register(ImpactActions)
class ImpactActionsAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ImpactActions._meta.get_fields()]
    list_per_page = 10
    ordering = ['event_date']


@admin.register(SovrnTransactions)
class SovrnTransactionsAdmin(admin.ModelAdmin):
    list_display = [field.name for field in SovrnTransactions._meta.get_fields()]
    list_per_page = 10
    ordering = ['commission_date']



@admin.register(CJTransactions)
class CJTransactionsAdmin(admin.ModelAdmin):
    list_display = [field.name for field in CJTransactions._meta.get_fields()]
    list_per_page = 10
    ordering = ['posting_date']





