# InvestTrack: Installation and Running Instructions

This document provides detailed instructions on how to set up and run the InvestTrack application.

## Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.8 or newer
- pip (Python package manager)
- Git (optional, for cloning the repository)

## Installation Steps

### 1. Clone or Download the Repository (if not already done)

```powershell
git clone <repository-url>
# Or download and extract the ZIP file manually
```

### 2. Navigate to the Project Directory

```powershell
cd "path\to\InvestTrack"
```

### 3. Set Up a Virtual Environment

Creating a virtual environment is recommended to avoid package conflicts:

```powershell
python -m venv venv
```

### 4. Activate the Virtual Environment

```powershell
.\venv\Scripts\Activate
```

### 5. Install Required Dependencies

Install all required packages using the requirements.txt file:

```powershell
pip install -r requirements.txt
```

### 6. Configure Alpha Vantage API Key

1. Sign up for a free Alpha Vantage API key at [Alpha Vantage](https://www.alphavantage.co/support/#api-key)
2. Open `investtrack/settings.py` and update the API key setting:

```python
# Alpha Vantage API settings
ALPHA_VANTAGE_API_KEY = 'your_api_key_here'
```

### 7. Set Up the Database

Run migrations to create the database schema:

```powershell
python manage.py migrate
```

### 8. Create an Admin User

Set up an administrator account to access the admin panel:

```powershell
python manage.py createsuperuser
```

Follow the prompts to create your username, email, and password.

### 9. Start the Development Server

Launch the Django development server:

```powershell
python manage.py runserver
```

### 10. Access the Application

- Open your web browser and navigate to: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- Access the admin panel at: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

## Using InvestTrack

1. **Register a new account** or log in with existing credentials
2. **Create portfolios** to organize your investments
3. **Search for stocks** using the market data search feature
4. **View detailed stock information** with price and volume charts
5. **Add assets to your portfolios** with purchase details
6. **Track performance** of your investments over time

## Troubleshooting

- **API Rate Limits**: Alpha Vantage free API has a limit of 25 API requests per day and 5 requests per minute
- **Database Issues**: If you encounter database errors, ensure migrations have been applied correctly
- **Missing Modules**: If you see import errors, verify that all dependencies are installed via requirements.txt

## Notes

- The application uses a fixed exchange rate (82.5 INR to 1 USD) for currency conversion
- For production use, consider upgrading to a paid Alpha Vantage API plan
