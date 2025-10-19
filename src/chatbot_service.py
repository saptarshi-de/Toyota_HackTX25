"""
Financial Advisor Chatbot Service using Google Gemini API
"""

import google.generativeai as genai
import os
import json
from typing import Dict, List, Optional, Tuple

class FinancialAdvisorChatbot:
    def __init__(self):
        """Initialize the chatbot with Gemini API"""
        # Set up Gemini API
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Chatbot state
        self.conversation_state = {
            'current_question': None,
            'collected_data': {},
            'question_flow': [
                'income',
                'credit_score', 
                'housing_status',
                'employment_status',
                'down_payment',
                'loan_preference',
                'vehicle_preference'
            ],
            'current_step': 0,
            'completed': False
        }
        
        # Question templates with options
        self.question_templates = {
            'income': {
                'question': "What's your annual household income? This helps us determine your budget range.",
                'type': 'range',
                'options': {
                    'min': 25000,
                    'max': 200000,
                    'step': 5000,
                    'default': 75000
                }
            },
            'credit_score': {
                'question': "What's your approximate credit score? This affects your interest rates significantly.",
                'type': 'range',
                'options': {
                    'min': 300,
                    'max': 850,
                    'step': 10,
                    'default': 700
                }
            },
            'housing_status': {
                'question': "What's your current housing situation?",
                'type': 'select',
                'options': [
                    {'value': 'own', 'label': 'Own (with mortgage)'},
                    {'value': 'own_outright', 'label': 'Own outright'},
                    {'value': 'rent', 'label': 'Rent'},
                    {'value': 'other', 'label': 'Other'}
                ]
            },
            'employment_status': {
                'question': "What's your employment status?",
                'type': 'select',
                'options': [
                    {'value': 'full-time', 'label': 'Full-time Employee'},
                    {'value': 'part-time', 'label': 'Part-time Employee'},
                    {'value': 'self-employed', 'label': 'Self-employed'},
                    {'value': 'contractor', 'label': 'Contractor'},
                    {'value': 'unemployed', 'label': 'Unemployed'},
                    {'value': 'retired', 'label': 'Retired'}
                ]
            },
            'down_payment': {
                'question': "How much can you put down as a down payment?",
                'type': 'number',
                'options': {
                    'min': 0,
                    'max': 50000,
                    'step': 500,
                    'default': 5000
                }
            },
            'loan_preference': {
                'question': "Do you prefer financing (buying) or leasing?",
                'type': 'select',
                'options': [
                    {'value': 'financing', 'label': 'Financing (Purchase)'},
                    {'value': 'lease', 'label': 'Leasing'},
                    {'value': 'either', 'label': 'Either is fine'}
                ]
            },
            'vehicle_preference': {
                'question': "What type of vehicle are you interested in?",
                'type': 'select',
                'options': [
                    {'value': 'sedan', 'label': 'Sedan'},
                    {'value': 'suv', 'label': 'SUV'},
                    {'value': 'hybrid', 'label': 'Hybrid/Electric'},
                    {'value': 'truck', 'label': 'Truck'},
                    {'value': 'any', 'label': 'Any type'}
                ]
            }
        }

    def start_conversation(self) -> Dict:
        """Start a new conversation and return the first question"""
        self.conversation_state = {
            'current_question': None,
            'collected_data': {},
            'question_flow': [
                'income',
                'credit_score', 
                'housing_status',
                'employment_status',
                'down_payment',
                'loan_preference',
                'vehicle_preference'
            ],
            'current_step': 0,
            'completed': False
        }
        
        return self._get_next_question()

    def process_response(self, user_response: str, session_id: str = None) -> Dict:
        """Process user response and return next question or recommendations"""
        if self.conversation_state['completed']:
            return self._generate_recommendations()
        
        current_question_key = self.conversation_state['question_flow'][self.conversation_state['current_step']]
        
        # Validate the user response
        validation_result = self._validate_response(user_response, current_question_key)
        
        if not validation_result['valid']:
            # Return validation error with helpful message
            return {
                'type': 'validation_error',
                'question': self.question_templates[current_question_key]['question'],
                'question_type': self.question_templates[current_question_key]['type'],
                'options': self.question_templates[current_question_key]['options'],
                'error_message': validation_result['message'],
                'step': self.conversation_state['current_step'] + 1,
                'total_steps': len(self.conversation_state['question_flow']),
                'help_text': validation_result.get('help_text', '')
            }
        
        # Store the validated response
        self.conversation_state['collected_data'][current_question_key] = validation_result['processed_value']
        
        # Move to next question
        self.conversation_state['current_step'] += 1
        
        if self.conversation_state['current_step'] >= len(self.conversation_state['question_flow']):
            self.conversation_state['completed'] = True
            return self._generate_recommendations()
        else:
            return self._get_next_question()

    def _validate_response(self, user_response: str, question_key: str) -> Dict:
        """Validate user response based on question type and return validation result"""
        user_response = user_response.strip()
        
        if not user_response:
            return {
                'valid': False,
                'message': "Please provide a response. I need this information to help you get the best financing options.",
                'help_text': "You can't leave this field empty."
            }
        
        # Check for obviously invalid responses
        invalid_responses = ['asdf', 'qwerty', '123', 'abc', 'test', 'hello', 'hi', 'yes', 'no', 'maybe', 'idk', 'dunno', 'whatever']
        if user_response.lower() in invalid_responses:
            return {
                'valid': False,
                'message': f"I understand you might be unsure, but '{user_response}' isn't a valid response for this question.",
                'help_text': "Please provide a real answer so I can help you properly."
            }
        
        # Question-specific validation
        if question_key == 'income':
            return self._validate_income(user_response)
        elif question_key == 'credit_score':
            return self._validate_credit_score(user_response)
        elif question_key == 'housing_status':
            return self._validate_housing_status(user_response)
        elif question_key == 'employment_status':
            return self._validate_employment_status(user_response)
        elif question_key == 'down_payment':
            return self._validate_down_payment(user_response)
        elif question_key == 'loan_preference':
            return self._validate_loan_preference(user_response)
        elif question_key == 'vehicle_preference':
            return self._validate_vehicle_preference(user_response)
        
        return {'valid': True, 'processed_value': user_response}
    
    def _validate_income(self, response: str) -> Dict:
        """Validate income input"""
        try:
            # Remove common currency symbols and commas
            cleaned = response.replace('$', '').replace(',', '').replace('k', '000').replace('K', '000')
            
            # Handle ranges like "50-60k"
            if '-' in cleaned:
                parts = cleaned.split('-')
                if len(parts) == 2:
                    low = float(parts[0].strip())
                    high = float(parts[1].strip())
                    income = (low + high) / 2
                else:
                    return {'valid': False, 'message': "Please enter a single income amount, not a range.", 'help_text': "Example: 75000 or 75k"}
            else:
                income = float(cleaned)
            
            if income < 10000:
                return {'valid': False, 'message': "That income seems too low for vehicle financing. Please enter your actual annual household income.", 'help_text': "Include all sources of income for your household."}
            elif income > 1000000:
                return {'valid': False, 'message': "That income seems unusually high. Please double-check and enter your actual annual household income.", 'help_text': "Enter your total household income before taxes."}
            
            return {'valid': True, 'processed_value': str(int(income))}
            
        except ValueError:
            return {'valid': False, 'message': "Please enter a valid income amount (numbers only).", 'help_text': "Examples: 75000, 75k, $75,000"}
    
    def _validate_credit_score(self, response: str) -> Dict:
        """Validate credit score input"""
        try:
            score = int(response)
            
            if score < 300:
                return {'valid': False, 'message': "Credit scores start at 300. Please enter a valid credit score.", 'help_text': "Credit scores range from 300 to 850."}
            elif score > 850:
                return {'valid': False, 'message': "Credit scores max out at 850. Please enter a valid credit score.", 'help_text': "Credit scores range from 300 to 850."}
            elif score < 500:
                return {'valid': False, 'message': f"A credit score of {score} is quite low. Are you sure this is correct?", 'help_text': "You can check your credit score for free at annualcreditreport.com"}
            
            return {'valid': True, 'processed_value': str(score)}
            
        except ValueError:
            return {'valid': False, 'message': "Please enter a valid credit score (numbers only).", 'help_text': "Credit scores are typically between 300-850."}
    
    def _validate_housing_status(self, response: str) -> Dict:
        """Validate housing status input"""
        valid_options = ['own', 'own_outright', 'rent', 'other']
        response_lower = response.lower()
        
        # Check for exact matches
        if response_lower in valid_options:
            return {'valid': True, 'processed_value': response_lower}
        
        # Check for partial matches
        if 'own' in response_lower and 'mortgage' in response_lower:
            return {'valid': True, 'processed_value': 'own'}
        elif 'own' in response_lower and ('outright' in response_lower or 'paid' in response_lower):
            return {'valid': True, 'processed_value': 'own_outright'}
        elif 'rent' in response_lower or 'renting' in response_lower:
            return {'valid': True, 'processed_value': 'rent'}
        
        return {'valid': False, 'message': f"I don't recognize '{response}' as a housing status. Please choose from the options provided.", 'help_text': "Select: Own (with mortgage), Own outright, Rent, or Other"}
    
    def _validate_employment_status(self, response: str) -> Dict:
        """Validate employment status input"""
        valid_options = ['full-time', 'part-time', 'self-employed', 'contractor', 'unemployed', 'retired']
        response_lower = response.lower()
        
        # Check for exact matches
        if response_lower in valid_options:
            return {'valid': True, 'processed_value': response_lower}
        
        # Check for partial matches
        if 'full' in response_lower and 'time' in response_lower:
            return {'valid': True, 'processed_value': 'full-time'}
        elif 'part' in response_lower and 'time' in response_lower:
            return {'valid': True, 'processed_value': 'part-time'}
        elif 'self' in response_lower and 'employ' in response_lower:
            return {'valid': True, 'processed_value': 'self-employed'}
        elif 'contract' in response_lower or 'freelance' in response_lower:
            return {'valid': True, 'processed_value': 'contractor'}
        elif 'unemploy' in response_lower or 'jobless' in response_lower:
            return {'valid': True, 'processed_value': 'unemployed'}
        elif 'retire' in response_lower:
            return {'valid': True, 'processed_value': 'retired'}
        
        return {'valid': False, 'message': f"I don't recognize '{response}' as an employment status. Please choose from the options provided.", 'help_text': "Select: Full-time Employee, Part-time Employee, Self-employed, Contractor, Unemployed, or Retired"}
    
    def _validate_down_payment(self, response: str) -> Dict:
        """Validate down payment input"""
        try:
            # Remove currency symbols and commas
            cleaned = response.replace('$', '').replace(',', '').replace('k', '000').replace('K', '000')
            amount = float(cleaned)
            
            if amount < 0:
                return {'valid': False, 'message': "Down payment can't be negative. Please enter a positive amount.", 'help_text': "Enter 0 if you don't have a down payment."}
            elif amount > 100000:
                return {'valid': False, 'message': "That's a very large down payment. Please double-check the amount.", 'help_text': "Most down payments are between $0-$50,000."}
            
            return {'valid': True, 'processed_value': str(int(amount))}
            
        except ValueError:
            return {'valid': False, 'message': "Please enter a valid down payment amount (numbers only).", 'help_text': "Examples: 5000, $5,000, 5k"}
    
    def _validate_loan_preference(self, response: str) -> Dict:
        """Validate loan preference input"""
        valid_options = ['financing', 'lease', 'either']
        response_lower = response.lower()
        
        # Check for exact matches
        if response_lower in valid_options:
            return {'valid': True, 'processed_value': response_lower}
        
        # Check for partial matches
        if 'buy' in response_lower or 'purchase' in response_lower or 'finance' in response_lower:
            return {'valid': True, 'processed_value': 'financing'}
        elif 'lease' in response_lower or 'rent' in response_lower:
            return {'valid': True, 'processed_value': 'lease'}
        elif 'both' in response_lower or 'any' in response_lower or 'doesn\'t matter' in response_lower:
            return {'valid': True, 'processed_value': 'either'}
        
        return {'valid': False, 'message': f"I don't recognize '{response}' as a loan preference. Please choose from the options provided.", 'help_text': "Select: Financing (Purchase), Leasing, or Either is fine"}
    
    def _validate_vehicle_preference(self, response: str) -> Dict:
        """Validate vehicle preference input"""
        valid_options = ['sedan', 'suv', 'hybrid', 'truck', 'any']
        response_lower = response.lower()
        
        # Check for exact matches
        if response_lower in valid_options:
            return {'valid': True, 'processed_value': response_lower}
        
        # Check for partial matches
        if 'car' in response_lower or 'sedan' in response_lower:
            return {'valid': True, 'processed_value': 'sedan'}
        elif 'suv' in response_lower or 'sport' in response_lower:
            return {'valid': True, 'processed_value': 'suv'}
        elif 'hybrid' in response_lower or 'electric' in response_lower or 'ev' in response_lower:
            return {'valid': True, 'processed_value': 'hybrid'}
        elif 'truck' in response_lower or 'pickup' in response_lower:
            return {'valid': True, 'processed_value': 'truck'}
        elif 'any' in response_lower or 'doesn\'t matter' in response_lower or 'no preference' in response_lower:
            return {'valid': True, 'processed_value': 'any'}
        
        return {'valid': False, 'message': f"I don't recognize '{response}' as a vehicle type. Please choose from the options provided.", 'help_text': "Select: Sedan, SUV, Hybrid/Electric, Truck, or Any type"}

    def _get_next_question(self) -> Dict:
        """Get the next question in the flow"""
        if self.conversation_state['completed']:
            return self._generate_recommendations()
        
        current_question_key = self.conversation_state['question_flow'][self.conversation_state['current_step']]
        question_template = self.question_templates[current_question_key]
        
        return {
            'type': 'question',
            'question': question_template['question'],
            'question_type': question_template['type'],
            'options': question_template['options'],
            'step': self.conversation_state['current_step'] + 1,
            'total_steps': len(self.conversation_state['question_flow'])
        }

    def _generate_recommendations(self) -> Dict:
        """Generate personalized recommendations using Gemini AI"""
        try:
            # Prepare context for Gemini
            user_data = self.conversation_state['collected_data']
            
            print(f"🤖 Attempting to generate AI recommendations with user data: {user_data}")
            
            prompt = f"""
            You are an expert Toyota Financial Services advisor with 15+ years of experience in automotive financing. You specialize in helping customers make optimal financial decisions for Toyota vehicle purchases and leases.

            CUSTOMER FINANCIAL PROFILE ANALYSIS:
            - Annual Income: ${user_data.get('income', 'Not provided')}
            - Credit Score: {user_data.get('credit_score', 'Not provided')}
            - Housing Status: {user_data.get('housing_status', 'Not provided')}
            - Employment Status: {user_data.get('employment_status', 'Not provided')}
            - Down Payment Available: ${user_data.get('down_payment', 'Not provided')}
            - Loan Preference: {user_data.get('loan_preference', 'Not provided')}
            - Vehicle Preference: {user_data.get('vehicle_preference', 'Not provided')}

            ANALYSIS FRAMEWORK - Apply these principles:

            1. DEBT-TO-INCOME ANALYSIS:
               - Calculate maximum monthly payment (typically 10-15% of monthly income)
               - Consider existing housing costs and other debts
               - Factor in employment stability and income growth potential

            2. CREDIT SCORE OPTIMIZATION:
               - Excellent (760+): Prime rates, best terms available
               - Good (660-759): Competitive rates, standard terms
               - Fair (580-659): Higher rates, may need larger down payment
               - Poor (<580): Subprime rates, significant down payment required

            3. FINANCING VS LEASING DECISION MATRIX:
               FINANCING BETTER WHEN:
               - Credit score 700+ (better rates)
               - High annual mileage (>15,000 miles)
               - Want to own the vehicle long-term
               - Can afford 20%+ down payment
               - Stable income and employment
               - Want to build equity

               LEASING BETTER WHEN:
               - Credit score 650-750 (lease rates often better)
               - Low annual mileage (<12,000 miles)
               - Want lower monthly payments
               - Prefer driving newer vehicles
               - Business use (tax benefits)
               - Uncertain about long-term needs

            4. TOYOTA-SPECIFIC CONSIDERATIONS:
               - Toyota Financial Services offers promotional rates (often 0.9%-2.9%)
               - Hybrid vehicles have better residual values for leasing
               - SUVs (RAV4, Highlander) hold value well for financing
               - Certified Pre-Owned programs available
               - Loyalty programs for existing Toyota owners

            5. RISK ASSESSMENT:
               - Employment stability (full-time vs contractor vs self-employed)
               - Housing stability (own vs rent)
               - Down payment adequacy (20%+ ideal, 10%+ acceptable)
               - Income-to-debt ratio analysis

            RECOMMENDATION REQUIREMENTS:
            Provide a comprehensive analysis that includes:

            1. PRIMARY RECOMMENDATION: Financing vs Leasing with specific reasoning
            2. FINANCIAL ANALYSIS: Debt-to-income assessment and affordability
            3. CREDIT OPTIMIZATION: Specific steps to improve credit score if needed
            4. TERM OPTIMIZATION: Ideal loan term based on financial profile
            5. DOWN PAYMENT STRATEGY: Optimal down payment amount and timing
            6. RISK MITIGATION: Address any financial concerns or red flags
            7. TOYOTA-SPECIFIC ADVANTAGES: Leverage Toyota Financial Services benefits

            Format your response as JSON with this structure:
            {{
                "recommendation": "Specific financing or leasing recommendation with brief reasoning",
                "reasoning": "Detailed financial analysis explaining the recommendation based on debt-to-income, credit score, employment stability, and Toyota-specific factors",
                "financial_analysis": {{
                    "debt_to_income_ratio": "calculated percentage and assessment",
                    "affordable_monthly_payment": "maximum recommended payment",
                    "credit_tier": "excellent/good/fair/poor with implications",
                    "risk_level": "low/medium/high with explanation"
                }},
                "tips": [
                    "Specific, actionable tip 1",
                    "Specific, actionable tip 2", 
                    "Specific, actionable tip 3",
                    "Toyota-specific tip or program"
                ],
                "suggested_terms": {{
                    "loan_term": "specific term recommendation (e.g., '60 months for optimal rate vs payment balance')",
                    "down_payment": "specific amount or percentage with reasoning",
                    "financing_type": "financing or lease with detailed justification",
                    "interest_rate_range": "expected rate range based on credit score"
                }},
                "concerns": [
                    "Any financial red flags or areas needing attention"
                ],
                "next_steps": [
                    "Immediate actionable step 1",
                    "Immediate actionable step 2",
                    "Toyota Financial Services specific action"
                ],
                "toyota_advantages": [
                    "Specific Toyota Financial Services benefits for this customer"
                ]
            }}

            Focus on practical, actionable advice that maximizes the customer's financial position while leveraging Toyota's financing advantages.
            """
            
            response = self.model.generate_content(prompt)
            
            print(f"🤖 Gemini API response received: {len(response.text)} characters")
            print(f"🤖 Response preview: {response.text[:200]}...")
            
            # Parse the JSON response
            try:
                recommendations = json.loads(response.text)
                print("✅ Successfully parsed JSON response from Gemini AI")
            except json.JSONDecodeError as json_error:
                print(f"JSON parsing error: {json_error}")
                print(f"Raw response: {response.text[:500]}...")
                # Generate personalized fallback based on user data
                recommendations = self._generate_personalized_fallback(user_data)
            
            return {
                'type': 'recommendations',
                'recommendations': recommendations,
                'user_data': user_data,
                'completed': True
            }
            
        except Exception as e:
            print(f"Error generating recommendations: {e}")
            # Generate personalized fallback based on user data
            recommendations = self._generate_personalized_fallback(user_data)
            return {
                'type': 'recommendations',
                'recommendations': recommendations,
                'user_data': user_data,
                'completed': True
            }

    def _generate_personalized_fallback(self, user_data: Dict) -> Dict:
        """Generate personalized recommendations based on user data when AI fails"""
        income = int(user_data.get('income', 75000))
        credit_score = int(user_data.get('credit_score', 700))
        housing_status = user_data.get('housing_status', 'rent')
        employment_status = user_data.get('employment_status', 'full-time')
        down_payment = int(user_data.get('down_payment', 5000))
        loan_preference = user_data.get('loan_preference', 'either')
        vehicle_preference = user_data.get('vehicle_preference', 'any')
        
        # Calculate debt-to-income ratio (simplified)
        monthly_income = income / 12
        max_monthly_payment = monthly_income * 0.15  # 15% rule
        
        # Determine credit tier
        if credit_score >= 760:
            credit_tier = "Excellent (760+)"
            risk_level = "Low"
            interest_rate_range = "0.9% - 2.9%"
        elif credit_score >= 660:
            credit_tier = "Good (660-759)"
            risk_level = "Low-Medium"
            interest_rate_range = "2.9% - 7.5%"
        elif credit_score >= 580:
            credit_tier = "Fair (580-659)"
            risk_level = "Medium"
            interest_rate_range = "7.5% - 12.0%"
        else:
            credit_tier = "Poor (<580)"
            risk_level = "High"
            interest_rate_range = "12.0% - 22.0%"
        
        # Generate personalized recommendation
        if credit_score >= 700 and income >= 60000:
            recommendation = "Financing (Purchase) is recommended for your profile"
            reasoning = f"With a {credit_score} credit score and ${income:,} income, you qualify for excellent rates. Financing allows you to build equity and own your vehicle long-term."
            suggested_financing_type = "financing"
        elif credit_score >= 650 and income >= 40000:
            recommendation = "Both financing and leasing are viable options"
            reasoning = f"Your {credit_score} credit score and ${income:,} income give you good options. Consider your driving habits and long-term goals."
            suggested_financing_type = loan_preference if loan_preference != 'either' else 'financing'
        else:
            recommendation = "Leasing may be more accessible for your current situation"
            reasoning = f"With a {credit_score} credit score, leasing often offers better approval rates and lower monthly payments than financing."
            suggested_financing_type = "lease"
        
        # Generate personalized tips
        tips = []
        if credit_score < 700:
            tips.append(f"Improve your credit score from {credit_score} to 700+ for better rates")
        if down_payment < income * 0.1:
            tips.append(f"Consider increasing your ${down_payment:,} down payment to 10-20% of vehicle price")
        if employment_status in ['part-time', 'contractor']:
            tips.append("Full-time employment typically provides better financing approval")
        if housing_status == 'rent':
            tips.append("Home ownership can improve your credit profile for future financing")
        
        # Add Toyota-specific tips
        if vehicle_preference == 'hybrid':
            tips.append("Toyota hybrids have excellent residual values - great for leasing")
        elif vehicle_preference == 'suv':
            tips.append("Toyota SUVs (RAV4, Highlander) hold value well for financing")
        
        tips.append("Explore Toyota Financial Services promotional rates and programs")
        
        # Generate concerns
        concerns = []
        if credit_score < 600:
            concerns.append(f"Credit score of {credit_score} may limit financing options")
        if income < 30000:
            concerns.append("Lower income may require larger down payment for approval")
        if employment_status == 'unemployed':
            concerns.append("Employment verification required for financing approval")
        
        # Generate next steps
        next_steps = [
            "Review your credit report for any errors",
            "Calculate your exact monthly budget for payments",
            "Compare Toyota Financial Services rates with other lenders"
        ]
        
        if suggested_financing_type == 'lease':
            next_steps.append("Consider mileage requirements for leasing")
        else:
            next_steps.append("Determine your ideal loan term (36-84 months)")
        
        # Toyota advantages
        toyota_advantages = [
            "Toyota Financial Services promotional rates (as low as 0.9%)",
            "Certified Pre-Owned programs with extended warranties",
            "Loyalty programs for existing Toyota customers"
        ]
        
        if vehicle_preference == 'hybrid':
            toyota_advantages.append("Toyota hybrid vehicles have excellent lease residuals")
        
        return {
            "recommendation": recommendation,
            "reasoning": reasoning,
            "financial_analysis": {
                "debt_to_income_ratio": f"Maximum affordable payment: ${max_monthly_payment:,.0f}/month (15% of income)",
                "affordable_monthly_payment": f"${max_monthly_payment:,.0f} per month maximum",
                "credit_tier": credit_tier,
                "risk_level": risk_level
            },
            "tips": tips,
            "suggested_terms": {
                "loan_term": "60 months for optimal rate vs payment balance",
                "down_payment": f"${down_payment:,} ({down_payment/income*100:.1f}% of income)",
                "financing_type": suggested_financing_type,
                "interest_rate_range": interest_rate_range
            },
            "concerns": concerns,
            "next_steps": next_steps,
            "toyota_advantages": toyota_advantages
        }

    def get_conversation_summary(self) -> Dict:
        """Get a summary of the current conversation"""
        return {
            'collected_data': self.conversation_state['collected_data'],
            'current_step': self.conversation_state['current_step'],
            'total_steps': len(self.conversation_state['question_flow']),
            'completed': self.conversation_state['completed']
        }

    def reset_conversation(self):
        """Reset the conversation state"""
        self.conversation_state = {
            'current_question': None,
            'collected_data': {},
            'question_flow': [
                'income',
                'credit_score', 
                'housing_status',
                'employment_status',
                'down_payment',
                'loan_preference',
                'vehicle_preference'
            ],
            'current_step': 0,
            'completed': False
        }
