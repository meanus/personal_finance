# finance_dashboard.py

import csv
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
import os
from typing import Dict

class PersonalFinanceDashboard:
    def __init__(self, csv_file: str = "mutual_fund_transactions.csv", starting_capital: float = 2000000, currency: str = "INR"):
        self.csv_file = csv_file
        self.starting_capital = starting_capital
        self.currency = currency
        # FIX: Changed date format to YYYY-MM-DD to match the CSV data.
        self.current_date = datetime.now().strftime("%Y-%m-%d")
        
        # Financial goals (customizable)
        self.financial_goals = {
            "target_portfolio_value": 500000,  # INR
            "monthly_savings_goal": 50000,     # INR
            "annual_income_goal": 1200000      # INR
        }
        
        # Initialize CSV if it doesn't exist
        self.initialize_csv()
    
    def initialize_csv(self):
        """Initialize CSV file with headers if it doesn't exist"""
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Date', 'Category', 'Type', 'Amount'])
                print(f"Created new {self.csv_file} file.")
    
    def read_transactions(self) -> pd.DataFrame:
        """Read transactions from CSV file"""
        try:
            df = pd.read_csv(self.csv_file)
            # FIX: Changed date format to '%Y-%m-%d' to correctly parse the dates from the CSV.
            df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
            df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
            return df
        except Exception as e:
            print(f"Error reading CSV file: {e}")
            return pd.DataFrame(columns=['Date', 'Category', 'Type', 'Amount'])
    
    def calculate_net_worth(self) -> Dict[str, float]:
        """Calculate net worth on a monthly basis"""
        df = self.read_transactions()
        if df.empty:
            return {
                "current_net_worth": self.starting_capital, 
                "current_cash": self.starting_capital, 
                "investment_value": 0
            }
        
        # FIX: Rewrote net worth logic for accuracy.
        # 1. Calculate the net change in cash from all transactions.
        total_income = df[df['Type'] == 'Income']['Amount'].sum()
        total_expenses = df[df['Type'] == 'Expense']['Amount'].sum()
        current_cash = self.starting_capital + total_income - total_expenses

        # 2. Get the current market value of investments.
        investment_value = self.get_investment_value()
        
        # 3. Net Worth is the sum of cash and investment value.
        current_net_worth = current_cash + investment_value
        
        # For the graph: Calculate cash balance over time.
        df['Month'] = df['Date'].dt.to_period('M')
        monthly_cash_flow = df.groupby('Month').apply(
            lambda x: x[x['Type'] == 'Income']['Amount'].sum() - x[x['Type'] == 'Expense']['Amount'].sum()
        ).cumsum()
        
        net_worth_data = {
            "starting_capital": self.starting_capital,
            "current_cash": current_cash,
            "investment_value": investment_value,
            "current_net_worth": current_net_worth,
            "monthly_cash_balance": monthly_cash_flow.to_dict() # Used for plotting cash trend
        }
        
        return net_worth_data
    
    def get_investment_value(self) -> float:
        """Calculate current investment value with a more accurate growth model."""
        df = self.read_transactions()
        if df.empty:
            return 0.0
        
        # Filter for only mutual fund investments.
        df_investments = df[
            (df['Category'].str.contains('Mutual Fund', case=False, na=False)) & 
            (df['Type'] == 'Expense')
        ].copy() # Use .copy() to avoid SettingWithCopyWarning
        
        if df_investments.empty:
            return 0.0
            
        # FIX: Calculate growth for each investment individually.
        # This is more accurate than the previous method.
        # (Assuming 12% annual return for demonstration)
        annual_return_rate = 0.12
        daily_return_rate = (1 + annual_return_rate)**(1/365) - 1 # More precise daily rate
        
        # Calculate how many days each investment has been held
        df_investments['days_held'] = (datetime.now() - df_investments['Date']).dt.days

        # Calculate the current value of each investment
        df_investments['current_value'] = df_investments.apply(
            lambda row: row['Amount'] * ((1 + daily_return_rate) ** row['days_held']),
            axis=1
        )
        
        # The total investment value is the sum of the current values
        return df_investments['current_value'].sum()

    
    def track_investment_portfolio(self) -> Dict[str, float]:
        """Track investment portfolio performance"""
        df = self.read_transactions()
        if df.empty:
            return {"total_invested": 0, "current_value": 0, "returns": 0, "return_percentage": 0}
        
        # Calculate investments by category
        investment_categories = df[
            df['Category'].str.contains('Investment|Mutual Fund', case=False, na=False)
        ]
        
        total_invested = investment_categories[investment_categories['Type'] == 'Expense']['Amount'].sum()
        current_value = self.get_investment_value()
        returns = current_value - total_invested
        return_percentage = (returns / total_invested * 100) if total_invested > 0 else 0
        
        portfolio_data = {
            "total_invested": total_invested,
            "current_value": current_value,
            "returns": returns,
            "return_percentage": return_percentage,
            "investment_breakdown": investment_categories.groupby('Category')['Amount'].sum().to_dict()
        }
        
        return portfolio_data
    
    def calculate_monthly_cashflow(self) -> Dict[str, Dict[str, float]]:
        """Calculate monthly cash flow (income vs expenses)"""
        df = self.read_transactions()
        if df.empty:
            return {}
        
        df['Month'] = df['Date'].dt.to_period('M')
        
        monthly_cashflow = {}
        # Sort months chronologically for the report
        for month in sorted(df['Month'].unique()):
            month_data = df[df['Month'] == month]
            income = month_data[month_data['Type'] == 'Income']['Amount'].sum()
            expenses = month_data[month_data['Type'] == 'Expense']['Amount'].sum()
            net_flow = income - expenses
            
            monthly_cashflow[str(month)] = {
                "income": income,
                "expenses": expenses,
                "net_flow": net_flow
            }
        
        return monthly_cashflow
    
    def track_financial_goals(self) -> Dict[str, Dict[str, float]]:
        """Track progress towards financial goals"""
        portfolio_data = self.track_investment_portfolio()
        cashflow_data = self.calculate_monthly_cashflow()
        
        # Calculate current year income
        df = self.read_transactions()
        current_year = datetime.now().year
        year_income = df[
            (df['Date'].dt.year == current_year) & 
            (df['Type'] == 'Income')
        ]['Amount'].sum()
        
        # Calculate average monthly savings
        if cashflow_data:
            all_net_flows = [data['net_flow'] for data in cashflow_data.values()]
            avg_monthly_savings = sum(all_net_flows) / len(all_net_flows) if all_net_flows else 0

        else:
            avg_monthly_savings = 0
        
        goal_progress = {
            "portfolio_goal": {
                "target": self.financial_goals["target_portfolio_value"],
                "current": portfolio_data["current_value"],
                "progress_percentage": min(100, (portfolio_data["current_value"] / self.financial_goals["target_portfolio_value"]) * 100) if self.financial_goals["target_portfolio_value"] > 0 else 0
            },
            "monthly_savings_goal": {
                "target": self.financial_goals["monthly_savings_goal"],
                "current": avg_monthly_savings,
                "progress_percentage": min(100, (avg_monthly_savings / self.financial_goals["monthly_savings_goal"]) * 100) if self.financial_goals["monthly_savings_goal"] > 0 else 0
            },
            "annual_income_goal": {
                "target": self.financial_goals["annual_income_goal"],
                "current": year_income,
                "progress_percentage": min(100, (year_income / self.financial_goals["annual_income_goal"]) * 100) if self.financial_goals["annual_income_goal"] > 0 else 0
            }
        }
        
        return goal_progress
    
    def add_new_transaction(self):
        """Add a new transaction for the current date"""
        print(f"\n=== Adding New Transaction for {self.current_date} ===")
        
        # Get transaction details from user
        category = input("Enter category (e.g., Groceries, Salary, Mutual Fund - Index): ").strip()
        
        while True:
            transaction_type = input("Enter type (Income/Expense): ").strip().title()
            if transaction_type in ['Income', 'Expense']:
                break
            print("Please enter either 'Income' or 'Expense'")
        
        while True:
            try:
                amount = float(input("Enter amount: ").strip())
                if amount > 0:
                    break
                else:
                    print("Amount must be positive")
            except ValueError:
                print("Please enter a valid number")
        
        # Add to CSV
        try:
            with open(self.csv_file, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([self.current_date, category, transaction_type, amount])
            
            print(f"✅ Transaction added successfully!")
            print(f"   Date: {self.current_date}")
            print(f"   Category: {category}")
            print(f"   Type: {transaction_type}")
            print(f"   Amount: {self.currency} {amount:,.2f}")
            
        except Exception as e:
            print(f"Error adding transaction: {e}")
    
    def display_dashboard(self):
        """Display comprehensive financial dashboard with visualizations"""
        print(f"\n{'='*60}")
        print(f"           PERSONAL FINANCE DASHBOARD")
        print(f"{'='*60}")
        
        # Get all data
        net_worth_data = self.calculate_net_worth()
        portfolio_data = self.track_investment_portfolio()
        cashflow_data = self.calculate_monthly_cashflow()
        goal_progress = self.track_financial_goals()
        
        # Display text summary
        print(f"\n📊 NET WORTH SUMMARY")
        print(f"   Current Net Worth: {self.currency} {net_worth_data['current_net_worth']:,.2f}")
        print(f"   Cash Balance: {self.currency} {net_worth_data['current_cash']:,.2f}")
        print(f"   Investments Value: {self.currency} {net_worth_data['investment_value']:,.2f}")
        
        print(f"\n💰 INVESTMENT PORTFOLIO")
        print(f"   Total Invested: {self.currency} {portfolio_data['total_invested']:,.2f}")
        print(f"   Current Value: {self.currency} {portfolio_data['current_value']:,.2f}")
        print(f"   Returns: {self.currency} {portfolio_data['returns']:,.2f}")
        print(f"   Return %: {portfolio_data['return_percentage']:.2f}%")
        
        print(f"\n🎯 GOAL PROGRESS")
        for goal_name, goal_data in goal_progress.items():
            print(f"   {goal_name.replace('_', ' ').title()}: {goal_data['progress_percentage']:.1f}% complete")
            print(f"     Current: {self.currency} {goal_data['current']:,.2f} | Target: {self.currency} {goal_data['target']:,.2f}")
        
        # Create visualizations
        self.create_visualizations(net_worth_data, portfolio_data, cashflow_data, goal_progress)
    
    def create_visualizations(self, net_worth_data, portfolio_data, cashflow_data, goal_progress):
        """Create matplotlib visualizations"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Personal Finance Dashboard', fontsize=16, fontweight='bold')
        
        # 1. Monthly Cash Flow
        if cashflow_data:
            months = [str(m) for m in cashflow_data.keys()] # Ensure keys are strings
            income = [data['income'] for data in cashflow_data.values()]
            expenses = [data['expenses'] for data in cashflow_data.values()]
            
            x = range(len(months))
            width = 0.35
            
            ax1.bar([i - width/2 for i in x], income, width, label='Income', color='green', alpha=0.7)
            ax1.bar([i + width/2 for i in x], expenses, width, label='Expenses', color='red', alpha=0.7)
            
            ax1.set_xlabel('Month')
            ax1.set_ylabel(f'Amount ({self.currency})')
            ax1.set_title('Monthly Income vs Expenses')
            ax1.set_xticks(x)
            # This method of setting labels and their properties at the same time is correct.
            ax1.set_xticklabels(months, rotation=45, ha="right")
            ax1.legend()
            ax1.grid(axis='y', linestyle='--', alpha=0.7)
        
        # 2. Cash Balance Trend Over Time
        if 'monthly_cash_balance' in net_worth_data and net_worth_data['monthly_cash_balance']:
            months = [str(m) for m in net_worth_data['monthly_cash_balance'].keys()]
            cash_values = [self.starting_capital + value for value in net_worth_data['monthly_cash_balance'].values()]
            
            ax2.plot(months, cash_values, marker='o', linewidth=2, markersize=6, color='blue')
            ax2.set_xlabel('Month')
            ax2.set_ylabel(f'Cash Balance ({self.currency})')
            ax2.set_title('Cash Balance Trend')

            # FIX: The 'ha' (horizontal alignment) parameter is not valid for tick_params.
            # It must be set on the labels directly using plt.setp().
            ax2.tick_params(axis='x', rotation=45)
            plt.setp(ax2.get_xticklabels(), ha="right")

            ax2.grid(True, linestyle='--', alpha=0.7)
        
        # 3. Goal Progress
        goals = [name.replace('_', ' ').title() for name in goal_progress.keys()]
        progress = [goal_progress[goal]['progress_percentage'] for goal in goal_progress.keys()]
        
        bars = ax3.barh(goals, progress, color=['#FF6B6B', '#4ECDC4', '#45B7D1'])
        ax3.set_xlabel('Progress (%)')
        ax3.set_title('Financial Goals Progress')
        ax3.set_xlim(0, 105) # Give a little space for labels
        
        for bar in bars:
            width = bar.get_width()
            ax3.text(width + 1, bar.get_y() + bar.get_height()/2, 
                    f'{width:.1f}%', ha='left', va='center')
        
        # 4. Portfolio Allocation
        if portfolio_data['investment_breakdown']:
            labels = list(portfolio_data['investment_breakdown'].keys())
            sizes = list(portfolio_data['investment_breakdown'].values())
            
            ax4.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140,
                   wedgeprops=dict(width=0.4)) # Donut chart
            ax4.set_title('Investment Portfolio Allocation')
            ax4.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        else:
            ax4.text(0.5, 0.5, 'No Investment Data', ha='center', va='center')
            ax4.set_title('Investment Portfolio Allocation')
        
        plt.tight_layout(rect=[0, 0, 1, 0.96]) # Adjust layout to make room for suptitle
        plt.show()
    
    def main_driver(self):
        """Main user interface"""
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
            print("7. Exit")
            print(f"{'='*50}")
            
            choice = input("Enter your choice (1-7): ").strip()
            
            if choice == '1':
                self.display_dashboard()
            
            elif choice == '2':
                self.add_new_transaction()
            
            elif choice == '3':
                net_worth_data = self.calculate_net_worth()
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
                for month, data in cashflow_data.items():
                    print(f"--- {month} ---")
                    print(f"     Income:   {self.currency} {data['income']:>12,.2f}")
                    print(f"     Expenses: {self.currency} {data['expenses']:>12,.2f}")
                    print(f"     Net Flow: {self.currency} {data['net_flow']:>12,.2f}")
            
            elif choice == '6':
                goal_progress = self.track_financial_goals()
                print(f"\n🎯 FINANCIAL GOALS PROGRESS")
                for goal_name, goal_data in goal_progress.items():
                    print(f"--- {goal_name.replace('_', ' ').title()} ---")
                    print(f"     Target:   {self.currency} {goal_data['target']:>12,.2f}")
                    print(f"     Current:  {self.currency} {goal_data['current']:>12,.2f}")
                    print(f"     Progress: {goal_data['progress_percentage']:.1f}%")
            
            elif choice == '7':
                print("\nThank you for using the Personal Finance Dashboard! 👋")
                break
            
            else:
                print("Invalid choice. Please enter a number between 1-7.")

# --- Main execution block ---
if __name__ == "__main__":
    # You can customize these parameters
    dashboard = PersonalFinanceDashboard(
        csv_file="mutual_fund_transactions.csv",
        starting_capital=2000000,  # 20 Lakh INR
        currency="INR"
    )
    
    # Start the application's main loop
    dashboard.main_driver()