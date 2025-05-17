from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.db.models import Sum
import csv
import json
import logging
from datetime import datetime, timedelta
from .models import Portfolio, Asset, MarketData
from .forms import (
    CustomUserCreationForm, PortfolioForm, AssetForm,
    StockSearchForm, DateRangeForm, ExportForm
)
from .services import AlphaVantageService

logger = logging.getLogger(__name__)

# Dashboard view
@login_required
def dashboard(request):
    portfolios = Portfolio.objects.filter(user=request.user)
    total_value = sum(portfolio.total_value() for portfolio in portfolios)
    total_investment = sum(portfolio.total_investment() for portfolio in portfolios)
    total_return = total_value - total_investment
    
    # Create data for chart
    portfolio_data = []
    for portfolio in portfolios:
        portfolio_data.append({
            'name': portfolio.name,
            'value': float(portfolio.total_value()),
        })
    
    context = {
        'portfolios': portfolios,
        'portfolio_count': portfolios.count(),
        'total_value': total_value,
        'total_investment': total_investment,
        'total_return': total_return,
        'return_percentage': (total_return / total_investment * 100) if total_investment else 0,
        'portfolio_data_json': json.dumps(portfolio_data),
    }
    return render(request, 'portfolio/dashboard.html', context)

# Portfolio views
@login_required
def portfolio_list(request):
    portfolios = Portfolio.objects.filter(user=request.user)
    context = {'portfolios': portfolios}
    return render(request, 'portfolio/portfolio_list.html', context)

@login_required
def portfolio_detail(request, pk):
    portfolio = get_object_or_404(Portfolio, pk=pk, user=request.user)
    assets = portfolio.assets.all()
    
    # Get or update asset prices
    av_service = AlphaVantageService()
    for asset in assets:
        if not asset.current_price or not asset.last_updated or \
           (timezone.now() - asset.last_updated > timedelta(hours=24)):
            av_service.update_asset_price(asset)
    
    # Prepare chart data
    asset_data = []
    for asset in assets:
        asset_data.append({
            'name': asset.name,
            'value': float(asset.current_value()),
            'profit_loss': float(asset.profit_loss()),
        })
    
    context = {
        'portfolio': portfolio,
        'assets': assets,
        'total_value': portfolio.total_value(),
        'total_investment': portfolio.total_investment(),
        'total_return': portfolio.total_return(),
        'return_percentage': portfolio.return_percentage(),
        'asset_data_json': json.dumps(asset_data),
    }
    return render(request, 'portfolio/portfolio_detail.html', context)

@login_required
def portfolio_create(request):
    if request.method == 'POST':
        form = PortfolioForm(request.POST)
        if form.is_valid():
            portfolio = form.save(commit=False)
            portfolio.user = request.user
            portfolio.save()
            messages.success(request, 'Portfolio created successfully!')
            return redirect('portfolio:portfolio_detail', pk=portfolio.pk)
    else:
        form = PortfolioForm()
    
    context = {'form': form, 'title': 'Create Portfolio'}
    return render(request, 'portfolio/portfolio_form.html', context)

@login_required
def portfolio_edit(request, pk):
    portfolio = get_object_or_404(Portfolio, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = PortfolioForm(request.POST, instance=portfolio)
        if form.is_valid():
            form.save()
            messages.success(request, 'Portfolio updated successfully!')
            return redirect('portfolio:portfolio_detail', pk=portfolio.pk)
    else:
        form = PortfolioForm(instance=portfolio)
    
    context = {'form': form, 'title': 'Edit Portfolio', 'portfolio': portfolio}
    return render(request, 'portfolio/portfolio_form.html', context)

@login_required
def portfolio_delete(request, pk):
    portfolio = get_object_or_404(Portfolio, pk=pk, user=request.user)
    
    if request.method == 'POST':
        portfolio.delete()
        messages.success(request, 'Portfolio deleted successfully!')
        return redirect('portfolio:portfolio_list')
    
    context = {'portfolio': portfolio}
    return render(request, 'portfolio/portfolio_confirm_delete.html', context)

# Asset views
@login_required
def asset_create(request, portfolio_id):
    portfolio = get_object_or_404(Portfolio, pk=portfolio_id, user=request.user)
    
    if request.method == 'POST':
        form = AssetForm(request.POST)
        if form.is_valid():
            asset = form.save(commit=False)
            asset.portfolio = portfolio
            
            # Validate the symbol and get current price from Alpha Vantage
            av_service = AlphaVantageService()
            quote = av_service.get_quote(asset.symbol)
            
            if quote and 'price' in quote:
                asset.current_price = quote['price']
                asset.last_updated = timezone.now()
                asset.save()
                messages.success(request, f'Asset {asset.name} added successfully!')
                return redirect('portfolio:portfolio_detail', pk=portfolio.pk)
            else:
                form.add_error('symbol', 'Unable to verify this stock symbol. Please check and try again.')
    else:
        form = AssetForm()
        
        # If symbol is provided via GET, pre-fill symbol and name
        symbol = request.GET.get('symbol', '')
        name = request.GET.get('name', '')
        if symbol and name:
            form = AssetForm(initial={'symbol': symbol, 'name': name})
    
    context = {
        'form': form, 
        'portfolio': portfolio,
        'title': 'Add Asset'
    }
    return render(request, 'portfolio/asset_form.html', context)

@login_required
def asset_detail(request, pk):
    asset = get_object_or_404(Asset, pk=pk, portfolio__user=request.user)
    
    # Update price if needed
    av_service = AlphaVantageService()
    if not asset.current_price or not asset.last_updated or \
       (timezone.now() - asset.last_updated > timedelta(hours=24)):
        av_service.update_asset_price(asset)
    
    # Get historical data
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)
    
    if request.method == 'POST':
        date_form = DateRangeForm(request.POST)
        if date_form.is_valid():
            start_date = date_form.cleaned_data['start_date']
            end_date = date_form.cleaned_data['end_date']
    else:
        date_form = DateRangeForm(initial={'start_date': start_date, 'end_date': end_date})
    
    # Get historical data from database or API
    historical_data = MarketData.objects.filter(
        symbol=asset.symbol, 
        date__range=(start_date, end_date)
    ).order_by('date')
    
    # If no data in DB or data is outdated, fetch from API
    if not historical_data or historical_data.count() < 5:
        av_service = AlphaVantageService()
        data = av_service.get_daily_time_series(asset.symbol)
        
        # Process and save the data
        historical_data = []
        for item in data:
            date_obj = datetime.strptime(item['date'], '%Y-%m-%d').date()
            if start_date <= date_obj <= end_date:
                market_data, created = MarketData.objects.get_or_create(
                    symbol=asset.symbol,
                    date=date_obj,
                    defaults={
                        'open_price': item['open'],
                        'high_price': item['high'],
                        'low_price': item['low'],
                        'close_price': item['close'],
                        'volume': item['volume']
                    }
                )
                historical_data.append(market_data)
        
        # Sort by date
        historical_data.sort(key=lambda x: x.date)
    
    # Prepare chart data
    chart_data = []
    for data in historical_data:
        chart_data.append({
            'date': data.date.strftime('%Y-%m-%d'),
            'price': float(data.close_price)
        })
    
    context = {
        'asset': asset,
        'date_form': date_form,
        'historical_data': historical_data,
        'chart_data_json': json.dumps(chart_data),
        'profit_loss': asset.profit_loss(),
        'roi_percentage': asset.roi_percentage(),
    }
    return render(request, 'portfolio/asset_detail.html', context)

@login_required
def asset_edit(request, pk):
    asset = get_object_or_404(Asset, pk=pk, portfolio__user=request.user)
    
    if request.method == 'POST':
        form = AssetForm(request.POST, instance=asset)
        if form.is_valid():
            updated_asset = form.save(commit=False)
            
            # Check if symbol changed, if so update current price
            if updated_asset.symbol != asset.symbol:
                av_service = AlphaVantageService()
                quote = av_service.get_quote(updated_asset.symbol)
                
                if quote and 'price' in quote:
                    updated_asset.current_price = quote['price']
                    updated_asset.last_updated = timezone.now()
                else:
                    form.add_error('symbol', 'Unable to verify this stock symbol. Please check and try again.')
                    context = {'form': form, 'asset': asset, 'title': 'Edit Asset'}
                    return render(request, 'portfolio/asset_form.html', context)
            
            updated_asset.save()
            messages.success(request, f'Asset {updated_asset.name} updated successfully!')
            return redirect('portfolio:asset_detail', pk=updated_asset.pk)
    else:
        form = AssetForm(instance=asset)
    
    context = {'form': form, 'asset': asset, 'title': 'Edit Asset'}
    return render(request, 'portfolio/asset_form.html', context)

@login_required
def asset_delete(request, pk):
    asset = get_object_or_404(Asset, pk=pk, portfolio__user=request.user)
    portfolio_id = asset.portfolio.id
    
    if request.method == 'POST':
        asset.delete()
        messages.success(request, 'Asset deleted successfully!')
        return redirect('portfolio:portfolio_detail', pk=portfolio_id)
    
    context = {'asset': asset}
    return render(request, 'portfolio/asset_confirm_delete.html', context)

# Market data and search views
@login_required
def market_data(request):
    form = StockSearchForm()
    context = {'form': form}
    return render(request, 'portfolio/market_data.html', context)

@login_required
def search_symbols(request):
    if request.method == 'GET':
        query = request.GET.get('symbol', '')
        if query:
            av_service = AlphaVantageService()
            results = av_service.search_symbol(query)
            return JsonResponse({'results': results})
    return JsonResponse({'results': []})

@login_required
def stock_details(request):
    """View for displaying detailed stock information with charts before adding to portfolio"""
    symbol = request.GET.get('symbol', '')
    company_name = request.GET.get('name', '')
    
    if not symbol:
        messages.error(request, "No stock symbol provided.")
        return redirect('portfolio:market_data')
    
    # Get stock quote and time series data
    av_service = AlphaVantageService()
    quote = av_service.get_quote(symbol)
    
    # Get historical data for chart
    time_series = av_service.get_daily_time_series(symbol)
    
    # Prepare chart data (last 30 days)
    chart_data = []
    for item in time_series[:30]:  # Limit to 30 days
        chart_data.append({
            'date': item['date'],
            'close': float(item['close']),
            'volume': item['volume']
        })
    
    # Reverse chart data to show chronological order
    chart_data.reverse()
    
    # Get list of portfolios for the add to portfolio dropdown
    portfolios = Portfolio.objects.filter(user=request.user)
    
    context = {
        'symbol': symbol,
        'company_name': company_name or symbol,
        'quote': quote,
        'chart_data_json': json.dumps(chart_data),
        'portfolios': portfolios,
    }
    
    return render(request, 'portfolio/stock_details.html', context)

# User profile view
@login_required
def user_profile(request):
    user = request.user
    portfolios = Portfolio.objects.filter(user=user)
    
    total_assets = Asset.objects.filter(portfolio__user=user).count()
    total_value = sum(portfolio.total_value() for portfolio in portfolios)
    
    context = {
        'user': user,
        'portfolios': portfolios,
        'total_assets': total_assets,
        'total_value': total_value,
    }
    return render(request, 'portfolio/profile.html', context)

# Export functionality
@login_required
def export_portfolio(request, pk):
    portfolio = get_object_or_404(Portfolio, pk=pk, user=request.user)
    assets = portfolio.assets.all()
    
    export_format = request.GET.get('format', 'csv')
    
    if export_format == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{portfolio.name}_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Symbol', 'Name', 'Type', 'Quantity', 'Purchase Price', 
                        'Purchase Date', 'Current Price', 'Current Value', 
                        'Profit/Loss', 'ROI %'])
        
        for asset in assets:
            writer.writerow([
                asset.symbol,
                asset.name,
                asset.get_asset_type_display(),
                asset.quantity,
                asset.purchase_price,
                asset.purchase_date,
                asset.current_price or 'N/A',
                asset.current_value(),
                asset.profit_loss(),
                f"{asset.roi_percentage():.2f}%",
            ])
        
        return response
    else:
        # PDF export would be implemented here
        # For now, we'll redirect back with an error message
        messages.error(request, 'PDF export is not yet implemented!')
        return redirect('portfolio:portfolio_detail', pk=portfolio.pk)

# User registration view
def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Your account has been created! You can now log in.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    
    context = {'form': form}
    return render(request, 'auth/register.html', context)

# API endpoint for symbol search autocomplete
@login_required
def symbol_search_api(request):
    """API endpoint to search for stock symbols by name or symbol"""
    query = request.GET.get('q', '')
    if not query or len(query) < 2:
        return JsonResponse({'results': []})
    
    av_service = AlphaVantageService()
    try:
        results = av_service.search_symbol(query)
        # Sort results by type
        results.sort(key=lambda x: x.get('type', ''))
        return JsonResponse({'results': results})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
