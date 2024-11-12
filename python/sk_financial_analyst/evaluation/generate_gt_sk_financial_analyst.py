import json
import os
from datetime import datetime
import yfinance as yf
import edgar

class FinancialDatesGroundTruth:
    def __init__(self, ticker, email_identity, form="10-Q"):
        self.ticker = ticker
        self.form = form
        edgar.set_identity(email_identity)
        
        # Initialize properties
        self.filings = None
        self.ten_q = None
        self.statements = {}
        self.dates = {}
        self.stock_data = {}
        self.values_for_metrics = {}
        self.metrics = {}

    def standardize_date(self, date_str):
        """Convert various date formats to YYYY-MM-DD format."""
        date_formats = ['%Y-%m-%d', '%b %d, %Y', '%B %d, %Y', '%Y%m%d']
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt).strftime('%Y-%m-%d')
            except ValueError:
                continue
        raise ValueError(f"Unable to parse date: {date_str}")

    def get_statement_date(self, date_str):
        """Convert YYYY-MM-DD to MMM DD, YYYY format for statement matching."""
        return datetime.strptime(date_str, '%Y-%m-%d').strftime('%b %d, %Y')

    def fetch_filing_data(self):
        """Fetch and process the latest filing data."""
        self.filings = edgar.Company(self.ticker).get_filings(form=self.form).latest(1)
        self.ten_q = self.filings.obj()
        
        # Store statement objects
        self.statements = {
            'balance_sheet': self.ten_q.balance_sheet,
            'income_statement': self.ten_q.income_statement,
            'cash_flow_statement': self.ten_q.cash_flow_statement
        }
        
        # Store dates from each statement
        for name, statement in self.statements.items():
            self.dates[f'{name}_dates'] = [
                self.standardize_date(str(date)) for date in statement.periods
            ]
        self.dates['filing_date'] = self.standardize_date(str(self.filings.report_date))

    def fetch_stock_prices(self):
        """Fetch historical stock prices for all statement dates."""
        stock = yf.Ticker(self.ticker)
        all_dates = {date for dates in self.dates.values() 
                    for date in (dates if isinstance(dates, list) else [dates])}
        
        for date_str in all_dates:
            date = datetime.strptime(date_str, "%Y-%m-%d")
            history = stock.history(start=date)
            if not history.empty:
                self.stock_data[date_str] = round(float(history.iloc[0]["Close"]), 2)

    def extract_financial_metrics(self):
        """Extract financial metrics from statements."""
        metrics_mapping = {
            'balance_sheet': {
                'total_current_assets': 'us-gaap_AssetsCurrent',
                'total_current_liabilities': 'us-gaap_LiabilitiesCurrent',
                'cash_and_cash_equivalents': 'us-gaap_CashAndCashEquivalentsAtCarryingValue',
                'marketable_securities': 'us-gaap_ShortTermInvestments',
                'accounts_receivable_net': 'us-gaap_AccountsReceivableNetCurrent',
                'total_liabilities': 'us-gaap_Liabilities',
                'total_stockholders_equity': 'us-gaap_StockholdersEquity',
                'long_term_debt': 'us-gaap_LongTermDebtNoncurrent'
            },
            'income_statement': {
                'revenue': 'us-gaap_RevenueFromContractWithCustomerExcludingAssessedTax',
                'cost_of_revenue': 'us-gaap_CostOfGoodsAndServicesSold',
                'net_income': 'us-gaap_NetIncomeLoss',
                'operating_income': 'us-gaap_OperatingIncomeLoss',
                'basic_earnings_per_share': 'us-gaap_EarningsPerShareBasic'
            },
            'cash_flow_statement': {
                'net_cash_from_operating_activities': 'us-gaap_NetCashProvidedByUsedInOperatingActivities',
                'capital_expenditures': 'us-gaap_PaymentsToAcquirePropertyPlantAndEquipment'
            }
        }

        for statement_type, metrics in metrics_mapping.items():
            statement = self.statements[statement_type]
            statement_dates = self.dates[f"{statement_type}_dates"]

            for metric_name, concept_code in metrics.items():
                self.values_for_metrics[metric_name] = {}
                concept = self._find_concept(statement, concept_code)
                
                if concept:
                    for date in statement_dates:
                        statement_date = self.get_statement_date(date)
                        value = concept.value.get(statement_date, 0)
                        if value:
                            self.values_for_metrics[metric_name][date] = float(str(value).replace(',', ''))

    def _find_concept(self, statement, concept_code):
        """Helper method to find concept in statement using various formats."""
        variants = [
            concept_code,
            concept_code.lower(),
            concept_code.replace('us-gaap_', ''),
            concept_code.replace('us-gaap_', '').lower()
        ]
        
        for variant in variants:
            try:
                return statement.get_concept(variant)
            except Exception:
                continue
        return None

    def calculate_financial_ratios(self):
        """Calculate financial ratios for each date."""
        for date in self.dates['balance_sheet_dates']:
            values = {k: v.get(date, 0) for k, v in self.values_for_metrics.items()}
            
            self.metrics[date] = {
                'balance_sheet_analysis': self._calculate_balance_sheet_ratios(values),
                'income_statement_analysis': self._calculate_income_statement_ratios(values),
                'cash_flow_analysis': self._calculate_cash_flow_ratios(values)
            }

    def _calculate_balance_sheet_ratios(self, values):
        if values['total_current_liabilities'] == 0:
            return {}
            
        return {
            'current_ratio': round(values['total_current_assets'] / values['total_current_liabilities'], 2),
            'quick_ratio': round((values['cash_and_cash_equivalents'] + 
                               values['marketable_securities'] + 
                               values['accounts_receivable_net']) / 
                               values['total_current_liabilities'], 2),
            'working_capital': "{:,}".format(int(values['total_current_assets'] - 
                                               values['total_current_liabilities'])),
            'debt_to_equity_ratio': round(values['total_liabilities'] / 
                                        max(values['total_stockholders_equity'], 1), 2)
        }

    def _calculate_income_statement_ratios(self, values):
        if values['revenue'] == 0:
            return {}
            
        return {
            'gross_margin': round((values['revenue'] - values['cost_of_revenue']) / 
                                values['revenue'] * 100, 2),
            'profit_margin': round(values['net_income'] / values['revenue'] * 100, 2),
            'operating_margin': round(values['operating_income'] / values['revenue'] * 100, 2),
            'return_on_equity': round(values['net_income'] / 
                                    max(values['total_stockholders_equity'], 1) * 100, 2)
        }

    def _calculate_cash_flow_ratios(self, values):
        total_debt = values['long_term_debt'] + values['total_current_liabilities']
        if total_debt == 0:
            return {}
            
        return {
            'cash_flow_to_debt_ratio': round(values['net_cash_from_operating_activities'] / 
                                           total_debt, 2),
            'free_cash_flow': "{:,}".format(int(values['net_cash_from_operating_activities'] + 
                                              values['capital_expenditures']))
        }

    def generate_ground_truth_json(self, output_dir=None):
        """Generate ground truth JSON file with all metrics and dates."""
        self.fetch_filing_data()
        self.fetch_stock_prices()
        self.extract_financial_metrics()
        self.calculate_financial_ratios()
        
        ground_truth_data = {
            'ticker': self.ticker,
            'filing_information': {
                'form_type': self.form,
                'filing_date': self.dates['filing_date'],
                'statement_dates': self.dates
            },
            'stock_prices': self.stock_data,
            'raw_financial_values': self.values_for_metrics,
            'financial_metrics': self.metrics
        }
        
        output_dir = output_dir or os.getcwd()
        output_filename = f"{self.ticker}_financial_dates_ground_truth_{datetime.now().strftime('%Y%m%d')}.json"
        output_path = os.path.join(output_dir, output_filename)
        
        with open(output_path, 'w') as f:
            json.dump(ground_truth_data, f, indent=4)
        
        return output_path

if __name__ == "__main__":
    generator = FinancialDatesGroundTruth(
        ticker="MSFT",
        email_identity="your.email@example.com"
    )
    json_path = generator.generate_ground_truth_json()