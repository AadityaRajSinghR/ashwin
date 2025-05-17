from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal

class Portfolio(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='portfolios')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.user.username}"
    
    def total_value(self):
        """Calculate the total current value of the portfolio"""
        return sum(asset.current_value() for asset in self.assets.all())
    
    def total_investment(self):
        """Calculate the total amount invested in the portfolio"""
        return sum(asset.total_cost() for asset in self.assets.all())
    
    def total_return(self):
        """Calculate the total return (profit/loss) of the portfolio"""
        return self.total_value() - self.total_investment()
    
    def return_percentage(self):
        """Calculate the percentage return of the portfolio"""
        investment = self.total_investment()
        if investment <= 0:
            return Decimal('0.00')
        return (self.total_return() / investment) * 100
    
    class Meta:
        ordering = ['-created_at']

class Asset(models.Model):
    ASSET_TYPES = (
        ('stock', 'Stock'),
        ('etf', 'ETF'),
        ('crypto', 'Cryptocurrency'),
        ('bond', 'Bond'),
        ('other', 'Other'),
    )
    
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='assets')
    symbol = models.CharField(max_length=10)  # Stock ticker symbol
    name = models.CharField(max_length=100)
    asset_type = models.CharField(max_length=10, choices=ASSET_TYPES, default='stock')
    quantity = models.DecimalField(max_digits=15, decimal_places=6)
    purchase_price = models.DecimalField(max_digits=15, decimal_places=2)  # Per unit
    purchase_date = models.DateField()
    notes = models.TextField(blank=True)
    current_price = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    last_updated = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.symbol} - {self.name} ({self.quantity})"
    
    def total_cost(self):
        """Calculate the total cost of this asset (purchase_price * quantity)"""
        return self.purchase_price * self.quantity
    
    def current_value(self):
        """Calculate the current value of this asset (current_price * quantity)"""
        if self.current_price:
            return self.current_price * self.quantity
        return self.purchase_price * self.quantity  # Use purchase price as fallback
    
    def profit_loss(self):
        """Calculate the profit or loss for this asset"""
        return self.current_value() - self.total_cost()
    
    def roi_percentage(self):
        """Calculate the ROI percentage for this asset"""
        if self.total_cost() <= 0:
            return Decimal('0.00')
        return (self.profit_loss() / self.total_cost()) * 100
    
    def update_price(self, price):
        """Update the current price of this asset"""
        self.current_price = price
        self.last_updated = timezone.now()
        self.save()
    
    class Meta:
        ordering = ['-purchase_date']
        unique_together = ['portfolio', 'symbol']

class MarketData(models.Model):
    """Optional model for caching market data to reduce API calls"""
    symbol = models.CharField(max_length=10)
    date = models.DateField()
    open_price = models.DecimalField(max_digits=15, decimal_places=2)
    high_price = models.DecimalField(max_digits=15, decimal_places=2)
    low_price = models.DecimalField(max_digits=15, decimal_places=2)
    close_price = models.DecimalField(max_digits=15, decimal_places=2)
    volume = models.BigIntegerField()
    
    def __str__(self):
        return f"{self.symbol} - {self.date} - {self.close_price}"
    
    class Meta:
        ordering = ['-date']
        unique_together = ['symbol', 'date']
