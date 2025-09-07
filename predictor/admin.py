from django.contrib import admin
from .models import CoinHistory

# Register your models here.
@admin.register(CoinHistory)
class CoinHistoryAdmin(admin.ModelAdmin):
    list_display = ['coin_symbol', 'timestamp', 'close_price', 'volume', 'created_at']
    list_filter = ['coin_symbol', 'timestamp']
    search_fields = ['coin_symbol']
    ordering = ['-timestamp']