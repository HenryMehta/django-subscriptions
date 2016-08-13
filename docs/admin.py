from django.contrib import admin
from models import Subscription, Category, SubscriptionCategory

class SubscriptionCategoryInline(admin.TabularInline):
    model = SubscriptionCategory
    extra = 1
    
class SubscriptionAdmin(admin.ModelAdmin):
    inlines = (SubscriptionCategoryInline,)
    search_fields = ('name', 'start', )

   
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(Category)
