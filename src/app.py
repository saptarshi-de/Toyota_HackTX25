from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
import os
import json
import csv # Import the csv module

# --- Vehicle Data Loading Function ---

# Define the relative path to the CSV file: from src/app.py up one level (..) then into data/
CSV_FILE_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'toyotacars.csv')

def load_vehicles_from_csv(file_path):
    """
    Loads vehicle data from a CSV file, mapping 'msrp_approx' to 'price'.
    """
    vehicles = []
    print(f"Attempting to load vehicle data from: {file_path}")
    try:
        # Use DictReader to treat each row as a dictionary with column headers as keys
        with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    # Convert MSRP to an integer for use as 'price'
                    price = int(row.get('msrp_approx', 0))
                    year = int(row.get('year', 0))
                except ValueError:
                    # Skip rows where MSRP or year cannot be converted
                    price = 0
                    year = 0

                if price > 0 and year > 0:
                    vehicle = {
                        "year": year,
                        "make": row.get('make', 'Toyota'),
                        "model": row.get('model', 'Unknown'),
                        "trim": row.get('trim', 'Base'),
                        "price": price, # Use 'msrp_approx' as the main price field
                        "body_type": row.get('body_type'),
                        "mpg_estimate": row.get('mpg_estimate')
                        # You can add more fields if needed
                    }
                    vehicles.append(vehicle)
        print(f"Successfully loaded {len(vehicles)} vehicles.")
    except FileNotFoundError:
        print(f"ERROR: CSV file not found at {file_path}. Please check your file path and structure.")
    except Exception as e:
        print(f"An unexpected error occurred while loading CSV: {e}")

    return vehicles

# Load the vehicle data when the app starts
TOYOTA_VEHICLES = load_vehicles_from_csv(CSV_FILE_PATH)

# --- Flask App Configuration ---

app = Flask(__name__,
            template_folder='templates',
            static_folder='static')
app.secret_key = 'toyota-financial-secret-key-2024'
CORS(app)

# --- Routes ---

@app.route('/')
def home():
    # Now TOYOTA_VEHICLES contains the data from the CSV file
    return render_template('home.html', vehicles=TOYOTA_VEHICLES)

@app.route('/preferences')
def preferences():
    return render_template('preferences.html')

@app.route('/survey')
def survey():
    return render_template('survey.html')

@app.route('/financing')
def financing():
    return render_template('financing.html')

@app.route('/compare')
def compare():
    return render_template('compare.html')

@app.route('/payment')
def payment():
    return render_template('payment.html')

@app.route('/api/calculate-payment', methods=['POST'])
def calculate_payment():
    data = request.json
    vehicle_price = data.get('vehicle_price', 0)
    down_payment = data.get('down_payment', 0)
    loan_term = data.get('loan_term', 60)  # months
    interest_rate = data.get('interest_rate', 5.5)  # annual percentage
    
    loan_amount = vehicle_price - down_payment
    monthly_rate = interest_rate / 100 / 12
    
    if monthly_rate > 0:
        # Standard annuity formula for monthly payment
        monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**loan_term) / ((1 + monthly_rate)**loan_term - 1)
    else:
        # Handle zero interest rate
        monthly_payment = loan_amount / loan_term
    
    total_payment = monthly_payment * loan_term
    total_interest = total_payment - loan_amount
    
    return jsonify({
        'monthly_payment': round(monthly_payment, 2),
        'total_payment': round(total_payment, 2),
        'total_interest': round(total_interest, 2),
        'loan_amount': loan_amount
    })

@app.route('/api/financing-options', methods=['POST'])
def get_financing_options():
    data = request.json
    credit_score = data.get('credit_score', 700)
    income = data.get('income', 50000)
    vehicle_price = data.get('vehicle_price', 30000)
    
    # Simulate different financing options based on credit score
    options = []
    
    if credit_score >= 750:
        options = [
            {"bank": "Toyota Financial", "rate": 3.9, "term": 60, "type": "financing"},
            {"bank": "Chase Auto", "rate": 4.2, "term": 60, "type": "financing"},
            {"bank": "Wells Fargo", "rate": 4.5, "term": 60, "type": "financing"},
            {"bank": "Toyota Financial", "rate": 2.9, "term": 36, "type": "lease"},
            {"bank": "Chase Auto", "rate": 3.2, "term": 36, "type": "lease"}
        ]
    elif credit_score >= 700:
        options = [
            {"bank": "Toyota Financial", "rate": 5.2, "term": 60, "type": "financing"},
            {"bank": "Chase Auto", "rate": 5.5, "term": 60, "type": "financing"},
            {"bank": "Wells Fargo", "rate": 5.8, "term": 60, "type": "financing"},
            {"bank": "Toyota Financial", "rate": 4.2, "term": 36, "type": "lease"},
            {"bank": "Chase Auto", "rate": 4.5, "term": 36, "type": "lease"}
        ]
    elif credit_score >= 650:
        options = [
            {"bank": "Toyota Financial", "rate": 6.8, "term": 60, "type": "financing"},
            {"bank": "Chase Auto", "rate": 7.2, "term": 60, "type": "financing"},
            {"bank": "Wells Fargo", "rate": 7.5, "term": 60, "type": "financing"},
            {"bank": "Toyota Financial", "rate": 5.8, "term": 36, "type": "lease"},
            {"bank": "Chase Auto", "rate": 6.2, "term": 36, "type": "lease"}
        ]
    else:
        options = [
            {"bank": "Toyota Financial", "rate": 8.5, "term": 60, "type": "financing"},
            {"bank": "Chase Auto", "rate": 9.2, "term": 60, "type": "financing"},
            {"bank": "Wells Fargo", "rate": 9.8, "term": 60, "type": "financing"},
            {"bank": "Toyota Financial", "rate": 7.5, "term": 36, "type": "lease"},
            {"bank": "Chase Auto", "rate": 8.2, "term": 36, "type": "lease"}
        ]
    
    # Calculate payments for each option
    for option in options:
        monthly_rate = option['rate'] / 100 / 12
        if option['type'] == 'financing':
            loan_amount = vehicle_price * 0.9  # Assume 10% down payment
            if monthly_rate > 0:
                monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**option['term']) / ((1 + monthly_rate)**option['term'] - 1)
            else:
                monthly_payment = loan_amount / option['term']
            option['monthly_payment'] = round(monthly_payment, 2)
            option['total_cost'] = round(monthly_payment * option['term'], 2)
        else:  # lease
            monthly_payment = vehicle_price * 0.01 * (1 + monthly_rate)  # Simplified lease calculation
            option['monthly_payment'] = round(monthly_payment, 2)
            option['total_cost'] = round(monthly_payment * option['term'], 2)
    
    return jsonify(options)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)
