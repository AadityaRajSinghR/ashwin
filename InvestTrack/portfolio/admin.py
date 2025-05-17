from django.contrib import admin
from .models import Portfolio, Asset, MarketData

class AssetInline(admin.TabularInline):
    model = Asset
    extra = 1

@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'created_at', 'total_value', 'total_return', 'return_percentage')
    list_filter = ('user', 'created_at')
    search_fields = ('name', 'user__username')
    inlines = [AssetInline]

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'name', 'portfolio', 'asset_type', 'quantity', 
                   'purchase_price', 'purchase_date', 'current_price', 'profit_loss', 'roi_percentage')
    list_filter = ('asset_type', 'purchase_date', 'portfolio')
    search_fields = ('symbol', 'name', 'portfolio__name')

@admin.register(MarketData)
class MarketDataAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'date', 'open_price', 'high_price', 'low_price', 'close_price', 'volume')
    list_filter = ('date', 'symbol')
    search_fields = ('symbol',)
