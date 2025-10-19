# Toyota Financial Services - Smart Vehicle Financing

A comprehensive web application that helps users find personalized financing and leasing options for Toyota vehicles based on their income, credit score, and preferences. Built for HackTX 2024.

## Features

- **AI Financial Advisor**: Sophisticated chatbot powered by Google Gemini AI with expert-level financial analysis, debt-to-income calculations, credit optimization strategies, and Toyota-specific recommendations
- **Vehicle Database**: Browse 2023-2024 Toyota models with transparent pricing
- **Smart Payment Calculator**: Get instant payment simulations based on your financial profile
- **Personalized Preferences**: Input lifestyle and vehicle preferences for better recommendations
- **Financial Survey**: Comprehensive income, credit score, and financial history assessment
- **Compare Options**: Side-by-side comparison of financing and leasing options from multiple lenders
- **Credit Score Insights**: Personalized tips to improve your credit score
- **Payment Integration**: Stripe API integration for secure payment processing
- **Mobile Responsive**: Works perfectly on all devices

## Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript
- **AI Integration**: Google Gemini API for intelligent financial advice
- **Payment Processing**: Stripe API
- **Styling**: Custom CSS with modern design principles

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set up Google Gemini API (for AI Chatbot)

1. Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Set the environment variable:
   ```bash
   export GEMINI_API_KEY=your_api_key_here
   ```
   Or create a `.env` file with:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

### 3. Run the Application

```bash
python3 run.py
```

The application will be available at `http://localhost:5002`

### 4. Stripe Integration (Optional)

For payment processing, set up Stripe:

1. Create a Stripe account at [stripe.com](https://stripe.com)
2. Get your publishable key from the Stripe dashboard
3. Replace `pk_test_your_stripe_publishable_key_here` in `payment.html` with your actual key
4. Set up webhook endpoints for payment confirmation

## Project Structure

```
Toyota_HackTX25/
├── src/                       # Source code directory
│   ├── __init__.py           # Package initialization
│   ├── app.py                # Flask application with API endpoints
│   ├── chatbot_service.py    # AI chatbot service using Gemini API
│   ├── templates/            # HTML templates
│   │   ├── home.html         # Vehicle browsing page
│   │   ├── preferences.html  # User preferences form
│   │   ├── survey.html       # Financial survey
│   │   ├── chatbot.html      # AI financial advisor chatbot
│   │   ├── financing.html    # Financing options display
│   │   ├── compare.html      # Options comparison
│   │   └── payment.html      # Payment processing
│   └── static/               # Static assets (CSS, JS, images)
│       ├── css/              # Stylesheets
│       └── js/               # JavaScript files
├── data/                     # Data files
│   ├── toyotacars.csv        # Toyota vehicle database
│   └── financeandlease.csv   # Financing options data
├── config.py                 # Configuration settings
├── run.py                    # Application entry point
├── requirements.txt          # Python dependencies
├── .gitignore               # Git ignore rules
└── README.md                # Project documentation
```

## App Flow

1. **Home Page**: Browse 2023-2024 Toyota vehicles with pricing
2. **AI Financial Advisor**: Interactive chatbot for personalized guidance (NEW!)
3. **Preferences**: Input lifestyle, budget, and vehicle preferences
4. **Survey**: Complete financial assessment (income, credit score, etc.)
5. **Financing**: View personalized financing and leasing options
6. **Compare**: Side-by-side comparison of all options
7. **Payment**: Complete purchase with Stripe integration

## API Endpoints

- `GET /` - Home page with vehicle database
- `GET /chatbot` - AI Financial Advisor chatbot interface
- `GET /preferences` - User preferences form
- `GET /survey` - Financial survey form
- `GET /financing` - Financing options display
- `GET /compare` - Options comparison
- `GET /payment` - Payment processing
- `POST /api/chatbot/start` - Start chatbot conversation
- `POST /api/chatbot/respond` - Process chatbot user response
- `POST /api/chatbot/summary` - Get conversation summary
- `POST /api/chatbot/reset` - Reset chatbot conversation
- `POST /api/calculate-payment` - Calculate monthly payments
- `POST /api/financing-options` - Get personalized financing options

## Current Status

✅ **Completed:**

- Complete app flow from vehicle selection to payment
- AI Financial Advisor chatbot with Google Gemini integration
- Toyota vehicle database with 2023-2024 models
- Personalized preferences and financial survey
- Smart payment calculator with real-time updates
- Financing options from multiple lenders
- Side-by-side comparison functionality
- Stripe payment integration (demo mode)
- Responsive design for all devices
- Professional UI/UX design

🚧 **Demo Features:**

- Payment processing is in demo mode (simulated)
- Real Stripe integration requires API key setup
- Financing options are simulated based on credit score

## Next Steps for Production

1. Set up real Stripe API keys and webhook endpoints
2. Integrate with actual lender APIs for real financing options
3. Add email notifications and confirmation system
4. Implement user accounts and application tracking
5. Add more detailed vehicle specifications and images
6. Integrate with Toyota's actual inventory system

## Hackathon Notes

This project was created for Toyota Financial Services at HackTX 2024. The focus is on creating a user-friendly platform that simplifies vehicle financing decisions through personalized recommendations and clear financial comparisons.

## Contributing

This is a hackathon project. For questions or suggestions, please contact the development team.

## Enhanced AI Prompt

The chatbot uses a sophisticated prompt engineering approach that transforms it into an expert-level financial advisor:

- **Expert Persona**: 15+ years of Toyota Financial Services experience
- **Comprehensive Analysis**: Debt-to-income, credit optimization, risk assessment
- **Decision Matrix**: Detailed financing vs leasing recommendations
- **Toyota-Specific Knowledge**: Promotional rates, vehicle-specific insights
- **Structured Output**: Professional-grade recommendations with actionable steps

See `ENHANCED_PROMPT_DOCUMENTATION.md` for detailed technical specifications.

## Demo

Visit `http://localhost:5002` to see the application in action!

**Key Features to Demo:**

1. **AI Financial Advisor**: Interactive chatbot for personalized guidance
2. Browse Toyota vehicles by year and type
3. Set preferences and budget range
4. Complete financial survey with credit score simulation
5. View personalized financing options
6. Compare options side-by-side
7. Complete payment process (demo mode)
