# transaction_manager.py

import csv

# Note: 'self' is removed. The function now takes the filename and date as arguments.
def add_new_transaction(csv_file: str, current_date: str):
    """Gets user input for a new transaction and appends it to the CSV file."""
    
    print(f"\n=== Adding New Transaction for {current_date} ===")
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
    
    # Use the provided arguments to write to the correct file
    try:
        with open(csv_file, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([current_date, category, transaction_type, amount])
        
        print(f"✅ Transaction added successfully!")
        
    except Exception as e:
        print(f"Error adding transaction: {e}")