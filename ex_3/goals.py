# goal_tracker.py

from datetime import datetime
from typing import Dict
import pandas as pd

# Note: 'self' is removed. All necessary data is now passed in as arguments.
def track_financial_goals(portfolio_data: Dict, cashflow_data: Dict, df: pd.DataFrame, financial_goals: Dict) -> Dict:
    """Track progress towards financial goals based on provided data."""
    
    # Calculate current year income from the provided DataFrame
    current_year = datetime.now().year
    year_income = df[
        (df['Date'].dt.year == current_year) & 
        (df['Type'] == 'Income')
    ]['Amount'].sum()
    
    # Calculate average monthly savings from the provided cashflow data
    if cashflow_data:
        all_net_flows = [data['net_flow'] for data in cashflow_data.values()]
        avg_monthly_savings = sum(all_net_flows) / len(all_net_flows) if all_net_flows else 0
    else:
        avg_monthly_savings = 0
    
    # Use the provided dictionaries to calculate goal progress
    goal_progress = {
        "portfolio_goal": {
            "target": financial_goals["target_portfolio_value"],
            "current": portfolio_data["current_value"],
            "progress_percentage": min(100, (portfolio_data["current_value"] / financial_goals["target_portfolio_value"]) * 100) if financial_goals["target_portfolio_value"] > 0 else 0
        },
        "monthly_savings_goal": {
            "target": financial_goals["monthly_savings_goal"],
            "current": avg_monthly_savings,
            "progress_percentage": min(100, (avg_monthly_savings / financial_goals["monthly_savings_goal"]) * 100) if financial_goals["monthly_savings_goal"] > 0 else 0
        },
        "annual_income_goal": {
            "target": financial_goals["annual_income_goal"],
            "current": year_income,
            "progress_percentage": min(100, (year_income / financial_goals["annual_income_goal"]) * 100) if financial_goals["annual_income_goal"] > 0 else 0
        }
    }
    
    return goal_progress