# InvestTrack: Portfolio Management & Market Analysis Tool

InvestTrack is a comprehensive Django-based web application that helps users manage investment portfolios, track stock performance, analyze market trends, and visualize data using the Alpha Vantage API.

## Features

- **Portfolio Management**: Create and manage multiple investment portfolios
- **Asset Tracking**: Add stocks and other assets to your portfolios with purchase details
- **Market Data Analysis**: Research stocks with price charts and volume data before adding to your portfolio
- **Stock Symbol Search**: Find stocks easily with an autocomplete search feature
- **Currency Conversion**: View values in both USD and INR
- **Interactive Visualizations**: Analyze your investments with charts and graphs
- **Performance Metrics**: Track ROI, profit/loss, and other key metrics

## Installation

### Prerequisites

- Python 3.8+
- pip (Python package manager)
- Git (optional, for cloning the repository)

### Setup Instructions

1. **Clone or download the repository**:
   ```
   git clone https://github.com/AadityaRajSinghR/ashwin.git
   ```
   Or download and extract the ZIP file.

2. **Navigate to the project directory**:
   ```
   cd InvestTrack
   ```

3. **Create a virtual environment** (optional but recommended):
   ```
   python -m venv venv
   ```

4. **Activate the virtual environment**:
   - Windows:
     ```
     .\venv\Scripts\activate
     ```
   - macOS/Linux:
     ```
     source venv/bin/activate
     ```

5. **Install dependencies**:
   ```
   pip install -r requirements.txt
   ```
   If the requirements.txt file doesn't exist, install Django and other dependencies manually:
   ```
   pip install django requests
   ```

6. **Configure Alpha Vantage API Key**:
   - Sign up for a free API key at [Alpha Vantage](https://www.alphavantage.co/support/#api-key)
   - Open `investtrack/settings.py` and add your API key:
     ```python
     # Alpha Vantage API settings
     ALPHA_VANTAGE_API_KEY = 'your_api_key_here'
     ```

7. **Run database migrations**:
   ```
   python manage.py migrate
   ```

8. **Create a superuser** (admin account):
   ```
   python manage.py createsuperuser
   ```
   Follow the prompts to set up your admin username, email, and password.

9. **Start the development server**:
   ```
   python manage.py runserver
   ```

10. **Access the application**:
    - Open your web browser and go to http://127.0.0.1:8000/
    - Access the admin panel at http://127.0.0.1:8000/admin/

## Usage

1. **Register and Login**:
   - Create a new account or login with your credentials

2. **Create a Portfolio**:
   - Navigate to Portfolios and create a new portfolio

3. **Add Assets**:
   - Search for stocks using the search feature
   - View detailed stock information and charts
   - Add stocks to your portfolio with purchase details

4. **Track Performance**:
   - Monitor your portfolio's overall performance
   - Analyze individual asset performance
   - View detailed charts and metrics

## Notes

- The application uses a fixed exchange rate (82.5 INR to 1 USD) for currency conversion
- Alpha Vantage free API has a limit of 25 API requests per day and 5 requests per minute
- For production use, consider upgrading to a paid API plan

## Project Structure

- `investtrack/` - Project configuration files
- `portfolio/` - Main application code
- `static/` - Static files (CSS, JavaScript)
- `templates/` - HTML templates
- `db.sqlite3` - SQLite database file

## Troubleshooting

- If you encounter API rate limit issues, the application will display appropriate error messages
- For any database errors, ensure migrations have been applied correctly

## Future Improvements

- Real-time exchange rates via API
- User-selectable preferred currency
- Additional visualization options for stock data
- Multi-factor authentication
- Portfolio sharing capabilities
