# analytics.py

import pandas as pd
from typing import Dict

def calculate_net_worth(df: pd.DataFrame, starting_capital: float, investment_value: float) -> Dict:
    """Calculates net worth, cash, and monthly trends from transaction data."""
    
    if df.empty:
        return {
            "starting_capital": starting_capital,
            "current_net_worth": starting_capital, 
            "current_cash": starting_capital, 
            "investment_value": 0,
            "monthly_cash_balance": {}
        }
    
    # Calculate current cash
    total_income = df[df['Type'] == 'Income']['Amount'].sum()
    total_expenses = df[df['Type'] == 'Expense']['Amount'].sum()
    current_cash = starting_capital + total_income - total_expenses

    # Calculate current net worth
    current_net_worth = current_cash + investment_value
    
    # Calculate monthly cash flow for the trend graph
    df['Month'] = df['Date'].dt.to_period('M')
    monthly_cash_flow = df.groupby('Month').apply(
        lambda x: x[x['Type'] == 'Income']['Amount'].sum() - x[x['Type'] == 'Expense']['Amount'].sum(), 
        include_groups=False
    ).cumsum()
    
    # Return all calculated values in a dictionary
    return {
        "starting_capital": starting_capital,
        "current_cash": current_cash,
        "investment_value": investment_value,
        "current_net_worth": current_net_worth,
        "monthly_cash_balance": monthly_cash_flow.to_dict()
    }