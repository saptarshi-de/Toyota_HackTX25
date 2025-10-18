from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
import os
import json

app = Flask(__name__)
app.secret_key = 'toyota-financial-secret-key-2024'
CORS(app)

# Toyota vehicle database
TOYOTA_VEHICLES = [
    {"year": 2024, "make": "Toyota", "model": "Camry", "trim": "LE", "price": 26520},
    {"year": 2024, "make": "Toyota", "model": "Camry", "trim": "XLE", "price": 31220},
    {"year": 2024, "make": "Toyota", "model": "Camry", "trim": "XSE", "price": 33820},
    {"year": 2024, "make": "Toyota", "model": "Corolla", "trim": "LE", "price": 22195},
    {"year": 2024, "make": "Toyota", "model": "Corolla", "trim": "XLE", "price": 25295},
    {"year": 2024, "make": "Toyota", "model": "Corolla", "trim": "SE", "price": 24195},
    {"year": 2024, "make": "Toyota", "model": "RAV4", "trim": "LE", "price": 28010},
    {"year": 2024, "make": "Toyota", "model": "RAV4", "trim": "XLE", "price": 32100},
    {"year": 2024, "make": "Toyota", "model": "RAV4", "trim": "XSE", "price": 36000},
    {"year": 2024, "make": "Toyota", "model": "Highlander", "trim": "LE", "price": 36820},
    {"year": 2024, "make": "Toyota", "model": "Highlander", "trim": "XLE", "price": 40220},
    {"year": 2024, "make": "Toyota", "model": "Highlander", "trim": "Limited", "price": 44820},
    {"year": 2024, "make": "Toyota", "model": "Prius", "trim": "LE", "price": 27545},
    {"year": 2024, "make": "Toyota", "model": "Prius", "trim": "XLE", "price": 30225},
    {"year": 2024, "make": "Toyota", "model": "Tacoma", "trim": "SR", "price": 27250},
    {"year": 2024, "make": "Toyota", "model": "Tacoma", "trim": "SR5", "price": 31250},
    {"year": 2024, "make": "Toyota", "model": "Tacoma", "trim": "TRD Off-Road", "price": 37250},
    {"year": 2024, "make": "Toyota", "model": "4Runner", "trim": "SR5", "price": 38105},
    {"year": 2024, "make": "Toyota", "model": "4Runner", "trim": "TRD Off-Road", "price": 42105},
    {"year": 2024, "make": "Toyota", "model": "4Runner", "trim": "Limited", "price": 47105},
    {"year": 2023, "make": "Toyota", "model": "Camry", "trim": "LE", "price": 25660},
    {"year": 2023, "make": "Toyota", "model": "Camry", "trim": "XLE", "price": 30160},
    {"year": 2023, "make": "Toyota", "model": "Corolla", "trim": "LE", "price": 21550},
    {"year": 2023, "make": "Toyota", "model": "Corolla", "trim": "XLE", "price": 24450},
    {"year": 2023, "make": "Toyota", "model": "RAV4", "trim": "LE", "price": 27225},
    {"year": 2023, "make": "Toyota", "model": "RAV4", "trim": "XLE", "price": 31115},
    {"year": 2023, "make": "Toyota", "model": "Highlander", "trim": "LE", "price": 35620},
    {"year": 2023, "make": "Toyota", "model": "Highlander", "trim": "XLE", "price": 39020},
    {"year": 2023, "make": "Toyota", "model": "Prius", "trim": "LE", "price": 27545},
    {"year": 2023, "make": "Toyota", "model": "Tacoma", "trim": "SR", "price": 26250},
    {"year": 2023, "make": "Toyota", "model": "Tacoma", "trim": "SR5", "price": 30250},
    {"year": 2023, "make": "Toyota", "model": "4Runner", "trim": "SR5", "price": 37105},
    {"year": 2023, "make": "Toyota", "model": "4Runner", "trim": "TRD Off-Road", "price": 41105}
]

@app.route('/')
def home():
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
        monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**loan_term) / ((1 + monthly_rate)**loan_term - 1)
    else:
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
    app.run(debug=True, host='0.0.0.0', port=5001)