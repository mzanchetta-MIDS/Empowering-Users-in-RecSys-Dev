# Capstone Spring 2025 - Zanchetta, Fenton, Heuberger, Siddiqui

This repo contains all the development files used to build our Capstone product. 


# Bookwise Recommendation System

As currently written, this repository has two main components:
1. A FastAPI backend that provides book recommendations
2. A Streamlit frontend that allows users to interact with the system

## Getting Started

### Prerequisites
- Python 3.10 or higher
- pip or poetry for package management

### Installation

Once you have the repository cloned: 

1. Set up a virtual environment 
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

### Running the Application Locally 

#### Step 1: Start the FastAPI Backend
```bash
cd API/210_api
uvicorn src.main:app --reload
```
The API will start running at http://127.0.0.1:8000

#### Step 2: Start the Streamlit Frontend
Open a new terminal window, navigate to the project root, and run:
```bash
cd streamlit_app
streamlit run app.py
```
The Streamlit app will open in your browser at http://localhost:8501

## Usage

1. When a user first opens the app, they'll be prompted to complete a short onboarding process
2. They provide information about reading preferences, favorite authors, genres, and additional context. 
3. Once complete, a user receives personalized book recommendations. 
4. Users interact with recommendations by saving, rating, or marking them as "not interested"
5. Every time the user generates a new batch of recommendations, their updated user profile information is sent to the recommendation model, and an explainable recommendation is received in return. 

## Development Notes

- The FastAPI backend provides endpoints for getting book information and processing user data
- The Streamlit frontend handles the user interface and interactions
- User profile information is stored locally and sent to the API for recommendation processing

