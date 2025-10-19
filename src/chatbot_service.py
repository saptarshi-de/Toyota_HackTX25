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
        
        # Store the response
        self.conversation_state['collected_data'][current_question_key] = user_response
        
        # Move to next question
        self.conversation_state['current_step'] += 1
        
        if self.conversation_state['current_step'] >= len(self.conversation_state['question_flow']):
            self.conversation_state['completed'] = True
            return self._generate_recommendations()
        else:
            return self._get_next_question()

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
            
            # Parse the JSON response
            try:
                recommendations = json.loads(response.text)
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                recommendations = {
                    "recommendation": "Based on your profile, we recommend exploring both financing and leasing options.",
                    "reasoning": "Your financial profile suggests you have good options available. We recommend comparing both financing and leasing to find the best fit for your situation.",
                    "financial_analysis": {
                        "debt_to_income_ratio": "Analysis unavailable - please complete financial assessment",
                        "affordable_monthly_payment": "Based on income, consider payments under 15% of monthly income",
                        "credit_tier": "Please provide credit score for accurate assessment",
                        "risk_level": "Medium - complete assessment needed for accurate risk evaluation"
                    },
                    "tips": [
                        "Consider improving your credit score for better rates",
                        "A larger down payment can reduce monthly payments",
                        "Compare financing vs leasing based on your driving habits",
                        "Explore Toyota Financial Services promotional rates"
                    ],
                    "suggested_terms": {
                        "loan_term": "60 months for optimal rate vs payment balance",
                        "down_payment": "10-20% of vehicle price for better rates",
                        "financing_type": "financing recommended for most customers",
                        "interest_rate_range": "Rate depends on credit score - excellent credit gets 0.9-2.9%"
                    },
                    "concerns": [],
                    "next_steps": [
                        "Complete detailed financial assessment",
                        "Review Toyota Financial Services options",
                        "Compare financing vs leasing scenarios"
                    ],
                    "toyota_advantages": [
                        "Toyota Financial Services promotional rates",
                        "Certified Pre-Owned programs",
                        "Loyalty programs for existing customers"
                    ]
                }
            
            return {
                'type': 'recommendations',
                'recommendations': recommendations,
                'user_data': user_data,
                'completed': True
            }
            
        except Exception as e:
            print(f"Error generating recommendations: {e}")
            return {
                'type': 'error',
                'message': 'Unable to generate recommendations at this time. Please try again.',
                'user_data': self.conversation_state['collected_data']
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
