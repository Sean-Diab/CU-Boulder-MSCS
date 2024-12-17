from flask import Flask, render_template
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime

app = Flask(__name__)

# Path to the CSV file
CSV_FILE = 'transactions.csv'

def load_and_process_data(csv_file):
    # Load CSV into pandas DataFrame
    df = pd.read_csv(csv_file)
    
    # Ensure 'date' is a datetime
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')

    # Categorize expenses based on keywords in 'description'
    # This is a very basic categorization. You can add more rules.
    def categorize(row):
        desc = row['description'].lower()
        amount = row['amount']
        if amount > 0:
            return 'Income'
        if 'rent' in desc:
            return 'Housing'
        elif 'electricity' in desc or 'internet' in desc:
            return 'Utilities'
        elif 'supermarket' in desc:
            return 'Groceries'
        elif 'restaurant' in desc or 'coffee' in desc:
            return 'Dining'
        elif 'gym' in desc:
            return 'Health & Fitness'
        else:
            return 'Other Expenses'
    
    df['category'] = df.apply(categorize, axis=1)
    
    return df

def get_summary_stats(df):
    # Calculate total income
    total_income = df[df['amount'] > 0]['amount'].sum()

    # Calculate total expenses
    total_expenses = df[df['amount'] < 0]['amount'].sum()

    # Calculate savings (income - absolute value of expenses)
    total_savings = total_income + total_expenses

    return total_income, total_expenses, total_savings

def plot_monthly_spending(df):
    # Group expenses by month (for expenses only)
    expenses_df = df[df['amount'] < 0].copy()
    expenses_df['month'] = expenses_df['date'].dt.to_period('M')
    monthly_expenses = expenses_df.groupby('month')['amount'].sum().reset_index()
    monthly_expenses['month_str'] = monthly_expenses['month'].astype(str)

    # Plot monthly spending chart
    plt.figure(figsize=(6,4))
    plt.bar(monthly_expenses['month_str'], monthly_expenses['amount'], color='red')
    plt.title('Monthly Spending')
    plt.xlabel('Month')
    plt.ylabel('Total Expenses')
    plt.tight_layout()

    # Save the plot
    output_path = os.path.join('static', 'monthly_spending.png')
    plt.savefig(output_path)
    plt.close()

    return 'monthly_spending.png'

@app.route('/')
def dashboard():
    df = load_and_process_data(CSV_FILE)
    total_income, total_expenses, total_savings = get_summary_stats(df)
    chart_filename = plot_monthly_spending(df)

    # Calculate category-wise expenses
    expense_categories = df[df['amount'] < 0].groupby('category')['amount'].sum().reset_index()
    # Convert to list of tuples for easy templating
    expense_details = [(row['category'], row['amount']) for _, row in expense_categories.iterrows()]

    return render_template('dashboard.html',
                           total_income=round(total_income, 2),
                           total_expenses=round(total_expenses, 2),
                           total_savings=round(total_savings, 2),
                           expense_details=expense_details,
                           chart_url='/static/' + chart_filename)

if __name__ == '__main__':
    # Run the Flask app
    app.run(debug=True)
