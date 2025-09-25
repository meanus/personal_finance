# visualizer.py

import matplotlib.pyplot as plt

def create_visualizations(net_worth_data, portfolio_data, cashflow_data, goal_progress, currency, starting_capital):
    """Create matplotlib visualizations for the finance dashboard."""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Personal Finance Dashboard', fontsize=16, fontweight='bold')

    # 1. Monthly Cash Flow
    if cashflow_data:
        months = [str(m) for m in cashflow_data.keys()]
        income = [data['income'] for data in cashflow_data.values()]
        expenses = [data['expenses'] for data in cashflow_data.values()]
        
        x = range(len(months))
        width = 0.35
        
        ax1.bar([i - width/2 for i in x], income, width, label='Income', color='green', alpha=0.7)
        ax1.bar([i + width/2 for i in x], expenses, width, label='Expenses', color='red', alpha=0.7)
        
        ax1.set_xlabel('Month')
        ax1.set_ylabel(f'Amount ({currency})')
        ax1.set_title('Monthly Income vs Expenses')
        ax1.set_xticks(x)
        ax1.set_xticklabels(months, rotation=45, ha="right")
        ax1.legend()
        ax1.grid(axis='y', linestyle='--', alpha=0.7)

    # 2. Cash Balance Trend Over Time
    if 'monthly_cash_balance' in net_worth_data and net_worth_data['monthly_cash_balance']:
        months = [str(m) for m in net_worth_data['monthly_cash_balance'].keys()]
        cash_values = [starting_capital + value for value in net_worth_data['monthly_cash_balance'].values()]
        
        ax2.plot(months, cash_values, marker='o', linewidth=2, markersize=6, color='blue')
        ax2.set_xlabel('Month')
        ax2.set_ylabel(f'Cash Balance ({currency})')
        ax2.set_title('Cash Balance Trend')
        ax2.tick_params(axis='x', rotation=45)
        plt.setp(ax2.get_xticklabels(), ha="right")
        ax2.grid(True, linestyle='--', alpha=0.7)

    # 3. Goal Progress
    goals = [name.replace('_', ' ').title() for name in goal_progress.keys()]
    progress = [goal_progress[goal]['progress_percentage'] for goal in goal_progress.keys()]
    
    bars = ax3.barh(goals, progress, color=['#FF6B6B', '#4ECDC4', '#45B7D1'])
    ax3.set_xlabel('Progress (%)')
    ax3.set_title('Financial Goals Progress')
    ax3.set_xlim(0, 105)
    
    for bar in bars:
        width = bar.get_width()
        ax3.text(width + 1, bar.get_y() + bar.get_height()/2, 
                f'{width:.1f}%', ha='left', va='center')

    # 4. Portfolio Allocation
    if portfolio_data['investment_breakdown']:
        labels = list(portfolio_data['investment_breakdown'].keys())
        sizes = list(portfolio_data['investment_breakdown'].values())
        
        ax4.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140,
               wedgeprops=dict(width=0.4))
        ax4.set_title('Investment Portfolio Allocation')
        ax4.axis('equal')
    else:
        ax4.text(0.5, 0.5, 'No Investment Data', ha='center', va='center')
        ax4.set_title('Investment Portfolio Allocation')
    
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.show()