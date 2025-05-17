from django.urls import path
from . import views

app_name = 'portfolio'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Portfolio management
    path('portfolios/', views.portfolio_list, name='portfolio_list'),
    path('portfolios/create/', views.portfolio_create, name='portfolio_create'),
    path('portfolios/<int:pk>/', views.portfolio_detail, name='portfolio_detail'),
    path('portfolios/<int:pk>/edit/', views.portfolio_edit, name='portfolio_edit'),
    path('portfolios/<int:pk>/delete/', views.portfolio_delete, name='portfolio_delete'),
    
    # Asset management
    path('portfolios/<int:portfolio_id>/assets/add/', views.asset_create, name='asset_create'),
    path('assets/<int:pk>/', views.asset_detail, name='asset_detail'),
    path('assets/<int:pk>/edit/', views.asset_edit, name='asset_edit'),
    path('assets/<int:pk>/delete/', views.asset_delete, name='asset_delete'),    # Market data and search
    path('market-data/', views.market_data, name='market_data'),
    path('search/', views.search_symbols, name='search_symbols'),
    path('api/symbol-search/', views.symbol_search_api, name='symbol_search_api'),
    path('stock-details/', views.stock_details, name='stock_details'),
    
    # User profile
    path('profile/', views.user_profile, name='profile'),
    
    # Export functionality
    path('portfolios/<int:pk>/export/', views.export_portfolio, name='export_portfolio'),
]
