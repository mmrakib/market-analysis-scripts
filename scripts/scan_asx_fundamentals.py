import requests
import pandas as pd

# Constants for Value Investing Thresholds
THRESHOLDS = {
    'P/E': 15,
    'P/B': 1,
    'Dividend_Yield': 0.03,  # 3%
    'ROE': 0.15,             # 15%
    'Debt_to_Equity': 1,
    'Margin_of_Safety': 0.20 # 20%
}

# Alpha Vantage API Key
API_KEY = 'N8YOA0OKGGR14MHP'  # Replace with your Alpha Vantage API key

def get_company_data(ticker):
    """Fetch company data from Alpha Vantage."""
    base_url = 'https://www.alphavantage.co/query'
    functions = ['OVERVIEW', 'INCOME_STATEMENT', 'BALANCE_SHEET', 'CASH_FLOW', 'GLOBAL_QUOTE']
    data = {}

    for function in functions:
        params = {
            'function': function,
            'symbol': ticker,
            'apikey': API_KEY
        }
        response = requests.get(base_url, params=params)
        result = response.json()

        if 'Note' in result or 'Error Message' in result:
            print(f"API limit reached or error for {ticker}. Message: {result.get('Note') or result.get('Error Message')}")
            return None

        data[function] = result

    return data

def calculate_metrics(ticker, data):
    """Calculate value investing metrics for a ticker."""
    try:
        # Extract necessary data
        overview = data['OVERVIEW']
        income_statement = data['INCOME_STATEMENT']['annualReports'][0]
        balance_sheet = data['BALANCE_SHEET']['annualReports'][0]
        cash_flow = data['CASH_FLOW']['annualReports'][0]
        global_quote_data = data['GLOBAL_QUOTE']

        # Ensure 'Global Quote' key exists
        if 'Global Quote' in global_quote_data:
            global_quote = global_quote_data['Global Quote']
            # Check if '05. price' exists in 'Global Quote'
            if '05. price' in global_quote:
                current_price = float(global_quote['05. price'])
            else:
                print(f"Price information is not available for {ticker}.")
                current_price = None
        else:
            print(f"Global Quote data is not available for {ticker}.")
            current_price = None

        if current_price is None:
            print(f"Cannot proceed with calculations without current price for {ticker}.")
            return None

        # P/E Ratio
        pe_ratio = float(overview.get('PERatio', 0))

        # P/B Ratio
        pb_ratio = float(overview.get('PriceToBookRatio', 0))

        # Dividend Yield
        dividend_yield = float(overview.get('DividendYield', 0))

        # ROE
        net_income = float(income_statement.get('netIncome', 0))
        shareholder_equity = float(balance_sheet.get('totalShareholderEquity', 0))
        roe = net_income / shareholder_equity if shareholder_equity != 0 else None

        # Debt to Equity Ratio
        total_debt = float(balance_sheet.get('totalLiabilities', 0))
        debt_to_equity = total_debt / shareholder_equity if shareholder_equity != 0 else None

        # Free Cash Flow
        operating_cash_flow = float(cash_flow.get('operatingCashflow', 0))
        capital_expenditures = float(cash_flow.get('capitalExpenditures', 0))
        fcf = operating_cash_flow - capital_expenditures

        # Intrinsic Value (DCF) Simplified
        shares_outstanding = float(overview.get('SharesOutstanding', 0))
        if shares_outstanding == 0:
            intrinsic_value = None
        else:
            # Assume constant FCF for simplicity
            discount_rate = 0.10  # 10%
            intrinsic_value = fcf / discount_rate / shares_outstanding

        # Margin of Safety
        if intrinsic_value and intrinsic_value != 0:
            margin_of_safety = (intrinsic_value - current_price) / intrinsic_value
        else:
            margin_of_safety = None

        # Compile metrics
        metrics = {
            'Company Name': overview.get('Name', 'N/A'),
            'Sector': overview.get('Sector', 'N/A'),
            'Description': overview.get('Description', 'N/A'),
            'Current Price': current_price,
            'P/E Ratio': pe_ratio,
            'P/B Ratio': pb_ratio,
            'Dividend Yield': dividend_yield,
            'Return on Equity (ROE)': roe,
            'Debt to Equity Ratio': debt_to_equity,
            'Free Cash Flow (FCF)': fcf,
            'Intrinsic Value per Share (DCF)': intrinsic_value,
            'Margin of Safety': margin_of_safety
        }
        return metrics
    except Exception as e:
        print(f"Error calculating metrics for {ticker}: {e}")
        return None


def interpret_metric(value, metric_name):
    """Interpret a single metric based on thresholds."""
    if value is None:
        return f"{metric_name}: Data not available."

    if metric_name == 'P/E Ratio':
        threshold = THRESHOLDS['P/E']
        if value > 0 and value < threshold:
            interpretation = f"{value:.2f} (Below threshold of {threshold}, potentially undervalued)"
        else:
            interpretation = f"{value:.2f} (Above threshold of {threshold}, may be overvalued)"
    elif metric_name == 'P/B Ratio':
        threshold = THRESHOLDS['P/B']
        if value > 0 and value < threshold:
            interpretation = f"{value:.2f} (Below threshold of {threshold}, potentially undervalued)"
        else:
            interpretation = f"{value:.2f} (Above threshold of {threshold}, may be overvalued or high intangible assets)"
    elif metric_name == 'Dividend Yield':
        threshold = THRESHOLDS['Dividend_Yield']
        if value > threshold:
            interpretation = f"{value*100:.2f}% (Above threshold of {threshold*100}%, attractive dividend)"
        else:
            interpretation = f"{value*100:.2f}% (Below threshold of {threshold*100}%, lower dividend yield)"
    elif metric_name == 'Return on Equity (ROE)':
        threshold = THRESHOLDS['ROE']
        if value > threshold:
            interpretation = f"{value*100:.2f}% (Above threshold of {threshold*100}%, strong profitability)"
        else:
            interpretation = f"{value*100:.2f}% (Below threshold of {threshold*100}%, weaker profitability)"
    elif metric_name == 'Debt to Equity Ratio':
        threshold = THRESHOLDS['Debt_to_Equity']
        if value < threshold:
            interpretation = f"{value:.2f} (Below threshold of {threshold}, healthy debt level)"
        else:
            interpretation = f"{value:.2f} (Above threshold of {threshold}, higher leverage)"
    elif metric_name == 'Margin of Safety':
        threshold = THRESHOLDS['Margin_of_Safety']
        if value > threshold:
            interpretation = f"{value*100:.2f}% (Above threshold of {threshold*100}%, good margin of safety)"
        else:
            interpretation = f"{value*100:.2f}% (Below threshold of {threshold*100}%, insufficient margin of safety)"
    else:
        interpretation = f"{value}"

    return f"{metric_name}: {interpretation}"

def is_undervalued(metrics):
    """Determine if a stock is undervalued based on thresholds."""
    conditions = []

    # P/E Ratio
    pe_ratio = metrics.get('P/E Ratio')
    if pe_ratio and pe_ratio > 0 and pe_ratio < THRESHOLDS['P/E']:
        conditions.append(True)
    else:
        conditions.append(False)

    # P/B Ratio
    pb_ratio = metrics.get('P/B Ratio')
    if pb_ratio and pb_ratio > 0 and pb_ratio < THRESHOLDS['P/B']:
        conditions.append(True)
    else:
        conditions.append(False)

    # Dividend Yield
    dividend_yield = metrics.get('Dividend Yield')
    if dividend_yield and dividend_yield > THRESHOLDS['Dividend_Yield']:
        conditions.append(True)
    else:
        conditions.append(False)

    # ROE
    roe = metrics.get('Return on Equity (ROE)')
    if roe and roe > THRESHOLDS['ROE']:
        conditions.append(True)
    else:
        conditions.append(False)

    # Debt to Equity Ratio
    debt_to_equity = metrics.get('Debt to Equity Ratio')
    if debt_to_equity and debt_to_equity < THRESHOLDS['Debt_to_Equity']:
        conditions.append(True)
    else:
        conditions.append(False)

    # Margin of Safety
    margin_of_safety = metrics.get('Margin of Safety')
    if margin_of_safety and margin_of_safety > THRESHOLDS['Margin_of_Safety']:
        conditions.append(True)
    else:
        conditions.append(False)

    return all(conditions)

def main():
    ticker = input("Enter the stock ticker symbol: ").upper()
    data = get_company_data(ticker)
    if data is None:
        return

    metrics = calculate_metrics(ticker, data)
    if metrics is None:
        return

    # Display Company Information
    print(f"\nCompany Information for {ticker}:")
    print(f"Name: {metrics['Company Name']}")
    print(f"Sector: {metrics['Sector']}")
    print(f"Description: {metrics['Description']}\n")

    # Display Metrics with Interpretation
    print("Value Investing Metrics and Interpretations:\n")
    metric_names = [
        'Current Price',
        'P/E Ratio',
        'P/B Ratio',
        'Dividend Yield',
        'Return on Equity (ROE)',
        'Debt to Equity Ratio',
        'Free Cash Flow (FCF)',
        'Intrinsic Value per Share (DCF)',
        'Margin of Safety'
    ]

    for name in metric_names:
        value = metrics.get(name)
        interpretation = interpret_metric(value, name)
        print(interpretation)

    # Determine if the stock is undervalued
    if is_undervalued(metrics):
        print(f"\nOverall Assessment: {ticker} appears to be undervalued based on the value investing criteria.")
    else:
        print(f"\nOverall Assessment: {ticker} does not appear to be undervalued based on the value investing criteria.")

if __name__ == '__main__':
    main()
