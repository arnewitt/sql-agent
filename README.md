# sql-agent
A short demo on how agentic systems enable natural language interaction with SQL databases, simplifying data queries and analysis.

# Features

- Natural Language Queries: Interact with a SQL database using natural language.
- LLM-Powered Agent: Uses OpenAI's GPT models to interpret and execute queries.
- Streamlit Interface: User-friendly chat interface for seamless interaction.

# Setup

**1. Install Dependencies**
```bash
pip install -r requirements.txt
```

**2. Populate the Database**
```bash
python populate_database.py
```

**3. Run the App**
```bash
streamlit run app.py
```

# Building and Running the Docker Image
Note: you must populate the Database before building the Container.

**1. Build the Docker Image**

```bash
docker build -t sql-agent-app .
```

**2. Run the Docker Container**

```bash
docker run -p 8501:8501 --name sql-agent-container sql-agent-app
```

# Accessing the App

Open your web browser and navigate to http://localhost:8501 to interact with the App.

# Usage
1. Enter your OpenAI API key and database path in the sidebar.
2. Start asking questions about the data.
    - Example: "List all customers who made purchases last week."

# Prerequisites
- Python 3.9 or higher
- OpenAI API Key