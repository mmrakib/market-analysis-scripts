import requests
import pandas as pd

def get_company_overview(ticker, api_key):
    """Fetch company overview data from Alpha Vantage."""
    url = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={api_key}'
    response = requests.get(url)
    data = response.json()
    return data

def get_income_statement(ticker, api_key):
    """Fetch income statement data from Alpha Vantage."""
    url = f'https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol={ticker}&apikey={api_key}'
    response = requests.get(url)
    data = response.json()
    return data

def get_cash_flow(ticker, api_key):
    """Fetch cash flow statement data from Alpha Vantage."""
    url = f'https://www.alphavantage.co/query?function=CASH_FLOW&symbol={ticker}&apikey={api_key}'
    response = requests.get(url)
    data = response.json()
    return data

def get_balance_sheet(ticker, api_key):
    """Fetch balance sheet data from Alpha Vantage."""
    url = f'https://www.alphavantage.co/query?function=BALANCE_SHEET&symbol={ticker}&apikey={api_key}'
    response = requests.get(url)
    data = response.json()
    return data

def get_stock_price(ticker, api_key):
    """Fetch current stock price data from Alpha Vantage."""
    url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={api_key}'
    response = requests.get(url)
    data = response.json()
    return data

def calculate_value_investing_metrics(ticker, api_key):
    """Calculate various value investing metrics for a given ticker."""
    # Get data from Alpha Vantage
    company_data = get_company_overview(ticker, api_key)
    income_data = get_income_statement(ticker, api_key)
    cash_flow_data = get_cash_flow(ticker, api_key)
    balance_sheet_data = get_balance_sheet(ticker, api_key)
    price_data = get_stock_price(ticker, api_key)

    # Check for valid response
    if 'Note' in company_data or 'Note' in income_data or 'Note' in cash_flow_data:
        print("API call frequency limit reached. Please try again later.")
        return
    if 'Error Message' in company_data or 'Error Message' in income_data or 'Error Message' in cash_flow_data:
        print("Invalid ticker symbol or API call error.")
        return

    try:
        # Extract necessary data
        # From company overview
        company_name = company_data.get('Name', 'N/A')
        description = company_data.get('Description', 'N/A')
        sector = company_data.get('Sector', 'N/A')

        market_cap = float(company_data.get('MarketCapitalization', 0))
        pe_ratio = float(company_data.get('PERatio', 0))
        pb_ratio = float(company_data.get('PriceToBookRatio', 0))
        dividend_yield = float(company_data.get('DividendYield', 0))
        eps = float(company_data.get('EPS', 0))
        beta = float(company_data.get('Beta', 1))
        shares_outstanding = float(company_data.get('SharesOutstanding', 0))

        # From income statement
        annual_reports_income = income_data['annualReports']
        net_income_list = [float(report['netIncome']) for report in annual_reports_income[:5]]
        net_income = net_income_list[0]

        # From cash flow statement
        annual_reports_cf = cash_flow_data['annualReports']
        operating_cash_flow_list = [float(report['operatingCashflow']) for report in annual_reports_cf[:5]]
        capital_expenditures_list = [float(report['capitalExpenditures']) for report in annual_reports_cf[:5]]
        operating_cash_flow = operating_cash_flow_list[0]
        capital_expenditures = capital_expenditures_list[0]

        # From balance sheet
        annual_reports_bs = balance_sheet_data['annualReports']
        total_debt_list = [float(report['totalLiabilities']) for report in annual_reports_bs[:5]]
        shareholder_equity_list = [float(report['totalShareholderEquity']) for report in annual_reports_bs[:5]]
        total_debt = total_debt_list[0]
        shareholder_equity = shareholder_equity_list[0]

        # Stock price
        current_price = float(price_data['Global Quote']['05. price'])

        # Calculate metrics
        # Return on Equity (ROE)
        roe = (net_income / shareholder_equity) * 100 if shareholder_equity != 0 else None

        # Debt to Equity Ratio
        debt_to_equity = total_debt / shareholder_equity if shareholder_equity != 0 else None

        # Free Cash Flow (FCF)
        free_cash_flow = operating_cash_flow - capital_expenditures

        # DCF (Simple estimation using average FCF growth rate)
        fcf_growth_rates = []
        for i in range(1, len(operating_cash_flow_list)):
            previous_fcf = operating_cash_flow_list[i-1] - capital_expenditures_list[i-1]
            current_fcf = operating_cash_flow_list[i] - capital_expenditures_list[i]
            growth_rate = (previous_fcf - current_fcf) / current_fcf
            fcf_growth_rates.append(growth_rate)
        average_fcf_growth = sum(fcf_growth_rates) / len(fcf_growth_rates) if fcf_growth_rates else 0

        projected_fcfs = [free_cash_flow * ((1 + average_fcf_growth) ** i) for i in range(1, 6)]
        terminal_value = projected_fcfs[-1] * 10  # Assuming exit multiple of 10
        discount_rate = 0.10  # 10%
        discounted_fcfs = [fcf / ((1 + discount_rate) ** i) for i, fcf in enumerate(projected_fcfs, start=1)]
        discounted_terminal_value = terminal_value / ((1 + discount_rate) ** 5)
        dcf_value = sum(discounted_fcfs) + discounted_terminal_value
        intrinsic_value_per_share = dcf_value / shares_outstanding if shares_outstanding != 0 else None

        # Dividend Discount Model (DDM)
        dividends_per_share = current_price * dividend_yield
        dividend_growth_rate = 0.05  # Assuming 5% growth rate

        if discount_rate != dividend_growth_rate and dividends_per_share != 0:
            ddm_intrinsic_value = dividends_per_share / (discount_rate - dividend_growth_rate)
        else:
            ddm_intrinsic_value = None

        # Margin of Safety
        if intrinsic_value_per_share and intrinsic_value_per_share != 0:
            margin_of_safety = ((intrinsic_value_per_share - current_price) / intrinsic_value_per_share) * 100
        else:
            margin_of_safety = None

        # Display the metrics
        print(f"\nCompany Information for {ticker.upper()}:")
        print(f"Name: {company_name}")
        print(f"Sector: {sector}")
        print(f"Description: {description}\n")
        print(f"\nValue Investing Metrics for {ticker.upper()}:")
        print(f"Market Capitalization: ${market_cap:,.2f}")
        print(f"P/E Ratio: {pe_ratio:.2f}")
        print(f"P/B Ratio: {pb_ratio:.2f}")
        print(f"Dividend Yield: {dividend_yield * 100:.2f}%")
        print(f"Earnings Per Share (EPS): ${eps:.2f}")
        print(f"Current Stock Price: ${current_price:.2f}")
        print(f"Return on Equity (ROE): {roe:.2f}%" if roe else "ROE: N/A")
        print(f"Debt to Equity Ratio: {debt_to_equity:.2f}" if debt_to_equity else "Debt to Equity Ratio: N/A")
        print(f"Free Cash Flow (FCF): ${free_cash_flow:,.2f}")
        print(f"Intrinsic Value per Share (DCF): ${intrinsic_value_per_share:.2f}" if intrinsic_value_per_share else "Intrinsic Value per Share (DCF): N/A")
        print(f"DDM Intrinsic Value: ${ddm_intrinsic_value:.2f}" if ddm_intrinsic_value else "DDM Intrinsic Value: N/A")
        print(f"Margin of Safety: {margin_of_safety:.2f}%" if margin_of_safety else "Margin of Safety: N/A")
    except Exception as e:
        print("An error occurred while calculating metrics:", e)

def main():
    api_key = 'N8YOA0OKGGR14MHP'  # Replace with your Alpha Vantage API key
    ticker = input("Enter the stock ticker symbol: ")
    calculate_value_investing_metrics(ticker, api_key)

if __name__ == "__main__":
    main()
