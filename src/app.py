from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
import os
import json
import csv
from dotenv import load_dotenv
from .chatbot_service import FinancialAdvisorChatbot

# Load environment variables from .env file
load_dotenv()

# --- File Paths ---
VEHICLES_CSV_FILE_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'toyotacars.csv')
FINANCE_CSV_FILE_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'financeandlease.csv')


# --- Data Loading and Parsing Helpers ---

def parse_rate_range(rate_string):
    """
    Parses a rate string (e.g., '1.99% - 4.99%') and returns a dict with min/max rates.
    Defaults to 99.0 for max rate if parsing fails.
    """
    default_rate = 99.0
    if not rate_string:
        return {'min': default_rate, 'max': default_rate}
    
    try:
        # Remove percentage signs and trim whitespace
        rate_string = rate_string.replace('%', '').strip()
        
        if ' - ' in rate_string:
            parts = [float(p.strip()) for p in rate_string.split(' - ') if p.strip()]
            min_rate = parts[0] if parts else default_rate
            max_rate = parts[-1] if len(parts) > 1 else min_rate
        else:
            # Handle single rate value (e.g., '13.49%')
            min_rate = float(rate_string)
            max_rate = min_rate
            
        return {'min': min_rate, 'max': max_rate}
    except ValueError:
        return {'min': default_rate, 'max': default_rate}

def load_vehicles_from_csv(file_path):
    """Loads vehicle data from the main CSV file."""
    vehicles = []
    try:
        with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    price = int(row.get('msrp_approx', 0))
                    year = int(row.get('year', 0))
                except ValueError:
                    price = 0
                    year = 0

                if price > 0 and year > 0:
                    vehicle = {
                        "year": year,
                        "make": row.get('make', 'Toyota'),
                        "model": row.get('model', 'Unknown'),
                        "trim": row.get('trim', 'Base'),
                        "price": price,
                        "body_type": row.get('body_type'),
                        "mpg_estimate": row.get('mpg_estimate')
                    }
                    vehicles.append(vehicle)
    except FileNotFoundError:
        print(f"ERROR: Vehicle CSV file not found at {file_path}")
    return vehicles

def load_financing_data(file_path):
    """Loads financing and lease options from the dedicated CSV file."""
    lenders = []
    try:
        with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                lenders.append(row)
    except FileNotFoundError:
        print(f"ERROR: Finance CSV file not found at {file_path}")
    return lenders

# Global data variables
TOYOTA_VEHICLES = load_vehicles_from_csv(VEHICLES_CSV_FILE_PATH)
FINANCING_LENDERS = load_financing_data(FINANCE_CSV_FILE_PATH)

# Initialize chatbot service
try:
    CHATBOT = FinancialAdvisorChatbot()
except ValueError as e:
    print(f"Warning: Chatbot not initialized - {e}")
    CHATBOT = None

# --- Flask App Configuration ---

app = Flask(__name__,
            template_folder='templates',
            static_folder='static')
app.secret_key = 'toyota-financial-secret-key-2024'
CORS(app)

# --- Routes ---

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

@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')

@app.route('/api/chatbot/start', methods=['POST'])
def chatbot_start():
    """Start a new chatbot conversation"""
    if not CHATBOT:
        return jsonify({'error': 'Chatbot service not available'}), 500
    
    try:
        response = CHATBOT.start_conversation()
        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chatbot/respond', methods=['POST'])
def chatbot_respond():
    """Process user response and get next question or recommendations"""
    if not CHATBOT:
        return jsonify({'error': 'Chatbot service not available'}), 500
    
    try:
        data = request.json
        user_response = data.get('response', '')
        
        if not user_response:
            return jsonify({'error': 'Response is required'}), 400
        
        response = CHATBOT.process_response(user_response)
        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chatbot/summary', methods=['GET'])
def chatbot_summary():
    """Get conversation summary"""
    if not CHATBOT:
        return jsonify({'error': 'Chatbot service not available'}), 500
    
    try:
        summary = CHATBOT.get_conversation_summary()
        return jsonify(summary)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chatbot/reset', methods=['POST'])
def chatbot_reset():
    """Reset chatbot conversation"""
    if not CHATBOT:
        return jsonify({'error': 'Chatbot service not available'}), 500
    
    try:
        CHATBOT.reset_conversation()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/calculate-payment', methods=['POST'])
def calculate_payment():
    data = request.json
    vehicle_price = data.get('vehicle_price', 0)
    down_payment = data.get('down_payment', 0)
    loan_term = data.get('loan_term', 60)  # months
    interest_rate = data.get('interest_rate', 5.5)  # annual percentage
    
    loan_amount = vehicle_price - down_payment
    monthly_rate = interest_rate / 100 / 12
    
    # Calculate monthly payment using the standard annuity formula
    if monthly_rate > 0:
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

def get_rate_column_name(credit_score):
    """Maps a credit score to the corresponding CSV column name for interest rate range."""
    if credit_score >= 760:
        return 'interest_rate_range_apy_excellent (760+)'
    elif credit_score >= 660:
        return 'interest_rate_range_apy_good (660-759)'
    elif credit_score >= 580:
        return 'interest_rate_range_apy_fair (580-659)'
    else:
        return 'interest_rate_range_apy_poor (<580)'


@app.route('/api/financing-options', methods=['POST'])
@app.route('/api/financing-options', methods=['POST'])
def get_financing_options():
    data = request.json
    credit_score = data.get('credit_score', 700)
    vehicle_price = data.get('vehicle_price', 30000)
    
    down_payment = vehicle_price * 0.1
    loan_amount = vehicle_price - down_payment
    
    rate_column = get_rate_column_name(credit_score)
    # Use a dictionary to group options by a combination key
    grouped_options = {} 
    
    for lender in FINANCING_LENDERS:
        lender_name = lender.get('lender_name', 'Unknown Lender').strip()

        # Get the min/max rates for the user's credit score tier
        rate_range = parse_rate_range(lender.get(rate_column))
        interest_rate_min = rate_range['min']
        interest_rate_max = rate_range['max']

        if interest_rate_min >= 99.0 or not lender.get('country_coverage', '').startswith('US'):
            continue

        try:
            terms_months = [int(t.strip()) for t in lender.get('typical_terms_months', '60, 72').split(',') if t.strip().isdigit()]
        except ValueError:
            terms_months = [60, 72]
            
        loan_types = [t.strip() for t in lender.get('loan_types_offered', '').split(',') if t.strip()]

        
        # --- Grouping Logic: Iterate over loan types and terms ---
        for loan_type in loan_types:
            standardized_loan_type = loan_type.lower()
            
            # Determine the major option type (financing or lease)
            # This is the primary separator
            if 'loan' in standardized_loan_type:
                major_type = "financing"
            elif 'lease' in standardized_loan_type:
                major_type = "lease"
            else:
                continue # Skip unknown types

            for term in terms_months:
                
                # The grouping key MUST now include the major type (financing or lease)
                # Key: Lender + Term + Min Rate + Max Rate + Major Type
                group_key = f"{lender_name.lower()}-{term}-{interest_rate_min}-{interest_rate_max}-{major_type}"

                if group_key not in grouped_options:
                    # --- Initial Calculation for a new group ---
                    monthly_rate = interest_rate_min / 100 / 12
                    
                    if major_type == 'financing':
                        # Payment calculation for a standard loan
                        if monthly_rate > 0:
                            monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**term) / ((1 + monthly_rate)**term - 1)
                        else:
                            monthly_payment = loan_amount / term
                        total_cost = monthly_payment * term + down_payment
                        
                    elif major_type == 'lease':
                        # Simplified lease calculation (1% rule approximation)
                        monthly_base = vehicle_price * 0.01 
                        monthly_payment = monthly_base * (1 + monthly_rate) 
                        total_cost = monthly_payment * term # Total lease payments

                    # --- Create the initial grouped option ---
                    grouped_options[group_key] = {
                        "bank": lender_name,
                        "rate_min": interest_rate_min,
                        "rate_max": interest_rate_max,
                        "term": term,
                        "type": major_type,
                        # Store all individual term descriptions to be joined later
                        "term_descriptions_list": set(), 
                        "monthly_payment": round(monthly_payment, 2),
                        "total_cost": round(total_cost, 2),
                    }

                # --- Aggregation Step ---
                # Add the specific product description to the set for this group
                current_descriptions = grouped_options[group_key]["term_descriptions_list"]
                current_descriptions.add(loan_type.strip())


    # --- Final Formatting and Cleanup ---
    final_options = []
    for key, option in grouped_options.items():
        
        # Join the list of descriptions into a single string for display (e.g., 'New Auto Loan, Used Auto Loan')
        option['term_description'] = ", ".join(sorted(list(option.pop("term_descriptions_list"))))
        
        final_options.append(option)
    
    # Sort options by monthly payment for best first, then by term
    final_options.sort(key=lambda x: (x['monthly_payment'], x['term']))

    return jsonify(final_options)
    
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5002))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug, host='0.0.0.0', port=port)
