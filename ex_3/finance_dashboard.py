# finance_dashboard.py

import csv
import pandas as pd
from datetime import datetime
import os
from typing import Dict

# Import the visualization function from the other file
from visual import create_visualizations
from goals import track_financial_goals
from transaction_manager import add_new_transaction
from analytics import calculate_net_worth
from rt_funds import fetch_stock_data

class PersonalFinanceDashboard:
    def __init__(self, csv_file: str = "mutual_fund_transactions.csv", starting_capital: float = 2000000, currency: str = "INR"):
        self.csv_file = csv_file
        self.starting_capital = starting_capital
        self.currency = currency
        # New transactions are always written in the consistent YYYY-MM-DD format
        self.current_date = datetime.now().strftime("%Y-%m-%d")
        
        self.financial_goals = {
            "target_portfolio_value": 500000,
            "monthly_savings_goal": 50000,
            "annual_income_goal": 1200000
        }
        
        self.initialize_csv()
    
    def initialize_csv(self):
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Date', 'Category', 'Type', 'Amount'])
                print(f"Created new {self.csv_file} file.")
    
    def read_transactions(self) -> pd.DataFrame:
        try:
            df = pd.read_csv(self.csv_file)
            # Use 'mixed' format to flexibly handle both YYYY-MM-DD and DD-MM-YYYY dates
            df['Date'] = pd.to_datetime(df['Date'], format='mixed')
            df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
            return df
        except Exception as e:
            print(f"Error reading CSV file: {e}")
            return pd.DataFrame(columns=['Date', 'Category', 'Type', 'Amount'])
    

    
    def get_investment_value(self) -> float:
        df = self.read_transactions()
        df_investments = df[(df['Category'].str.contains('Mutual Fund', case=False, na=False)) & (df['Type'] == 'Expense')].copy()
        
        if df_investments.empty:
            return 0.0
            
        annual_return_rate = 0.12
        daily_return_rate = (1 + annual_return_rate)**(1/365) - 1
        
        df_investments['days_held'] = (datetime.now() - df_investments['Date']).dt.days
        df_investments['current_value'] = df_investments.apply(lambda row: row['Amount'] * ((1 + daily_return_rate) ** row['days_held']), axis=1)
        
        return df_investments['current_value'].sum()

    def track_investment_portfolio(self) -> Dict[str, float]:
        df = self.read_transactions()
        investment_categories = df[df['Category'].str.contains('Investment|Mutual Fund', case=False, na=False)]
        
        total_invested = investment_categories[investment_categories['Type'] == 'Expense']['Amount'].sum()
        current_value = self.get_investment_value()
        returns = current_value - total_invested
        return_percentage = (returns / total_invested * 100) if total_invested > 0 else 0
        
        return {
            "total_invested": total_invested,
            "current_value": current_value,
            "returns": returns,
            "return_percentage": return_percentage,
            "investment_breakdown": investment_categories.groupby('Category')['Amount'].sum().to_dict()
        }
    
    def calculate_monthly_cashflow(self) -> Dict[str, Dict[str, float]]:
        df = self.read_transactions()
        if df.empty: return {}
        
        df['Month'] = df['Date'].dt.to_period('M')
        monthly_cashflow = {}
        for month in sorted(df['Month'].unique()):
            month_data = df[df['Month'] == month]
            income = month_data[month_data['Type'] == 'Income']['Amount'].sum()
            expenses = month_data[month_data['Type'] == 'Expense']['Amount'].sum()
            monthly_cashflow[str(month)] = {"income": income, "expenses": expenses, "net_flow": income - expenses}
        
        return monthly_cashflow
    
    
    
    
    
    def display_dashboard(self):
        print(f"\n{'='*60}\n           PERSONAL FINANCE DASHBOARD\n{'='*60}")
        
        # First, gather all the necessary data
        df = self.read_transactions()
        
        portfolio_data = self.track_investment_portfolio()
        cashflow_data = self.calculate_monthly_cashflow()
        investment_value = self.get_investment_value()
        
        # Now, call the new, independent function with the data
        net_worth_data = calculate_net_worth(df, self.starting_capital, investment_value)
        goal_progress = track_financial_goals(portfolio_data, cashflow_data, df, self.financial_goals)
        
        # ... (the rest of the method's print statements are the same)
     
        
        create_visualizations(net_worth_data, portfolio_data, cashflow_data, goal_progress, self.currency, self.starting_capital)
    
    def main_driver(self):
        while True:
            print(f"\n{'='*50}")
            print("    PERSONAL FINANCE DASHBOARD")
            print(f"{'='*50}")
            print("1. View Dashboard Summary & Charts")
            print("2. Add New Transaction")
            print("3. View Net Worth Details")
            print("4. View Investment Portfolio Details")
            print("5. View Monthly Cash Flow Report")
            print("6. View Goal Progress Details")
            print("7. fetch stock data")
            print("8. Exit")
            print(f"{'='*50}")
            
            choice = input("Enter your choice (1-7): ").strip()
            
            if choice == '1':
                self.display_dashboard()

            elif choice == '2':
                # OLD CALL: self.add_new_transaction()
                # NEW CALL: Call the independent function and pass it the data it needs.
                add_new_transaction(self.csv_file, self.current_date)
            
            # ... (the rest of the choices are the same) ...
            elif choice == '3':
                df = self.read_transactions()
                investment_value = self.get_investment_value()
                
                net_worth_data = calculate_net_worth(df, self.starting_capital, investment_value)
                
                print(f"\n📊 NET WORTH ANALYSIS")
                print(f"   Starting Capital: {self.currency} {net_worth_data['starting_capital']:,.2f}")
                print(f"   Current Cash Balance: {self.currency} {net_worth_data['current_cash']:,.2f}")
                print(f"   Current Investment Value: {self.currency} {net_worth_data['investment_value']:,.2f}")
                print("-" * 30)
                print(f"   Total Net Worth: {self.currency} {net_worth_data['current_net_worth']:,.2f}")
            elif choice == '4':
                portfolio_data = self.track_investment_portfolio()
                print(f"\n💰 INVESTMENT PORTFOLIO")
                print(f"   Total Amount Invested: {self.currency} {portfolio_data['total_invested']:,.2f}")
                print(f"   Current Portfolio Value: {self.currency} {portfolio_data['current_value']:,.2f}")
                print(f"   Total Returns: {self.currency} {portfolio_data['returns']:,.2f}")
                print(f"   Return Percentage: {portfolio_data['return_percentage']:.2f}%")
                
                if portfolio_data['investment_breakdown']:
                    print(f"\n   Investment Breakdown (by cost):")
                    for category, amount in portfolio_data['investment_breakdown'].items():
                        print(f"     - {category}: {self.currency} {amount:,.2f}")
                        
                        
            elif choice == '5':
                cashflow_data = self.calculate_monthly_cashflow()
                print(f"\n💸 MONTHLY CASH FLOW REPORT")
                for month, values in cashflow_data.items():
                    print(f"--- {month} ---")
                    print(f"     Income:   {self.currency} {values['income']:>12,.2f}")
                    print(f"     Expenses: {self.currency} {values['expenses']:>12,.2f}")
                    print(f"     Net Flow: {self.currency} {values['net_flow']:>12,.2f}")
                    
            elif choice == '6':
                df = self.read_transactions()
                portfolio_data = self.track_investment_portfolio()
                cashflow_data = self.calculate_monthly_cashflow()
                goal_data = track_financial_goals(portfolio_data, cashflow_data, df, self.financial_goals)
                
                print(f"\n🎯 FINANCIAL GOALS PROGRESS")
                for name, values in goal_data.items():
                    print(f"--- {name.replace('_', ' ').title()} ---")
                    print(f"     Target:   {self.currency} {values['target']:>12,.2f}")
                    print(f"     Current:  {self.currency} {values['current']:>12,.2f}")
                    print(f"     Progress: {values['progress_percentage']:.1f}%")
                    
            elif choice == '7':
               
                fetch_stock_data()
            
            elif choice == '8':
                print("\nThank you for using the Personal Finance Dashboard! 👋")
                break
            else:
                print("Invalid choice. Please enter a number between 1-7.")
if __name__ == "__main__":
    dashboard = PersonalFinanceDashboard(
        csv_file="mutual_fund_transactions.csv",
        starting_capital=2000000,
        currency="INR"
    )
    dashboard.main_driver()