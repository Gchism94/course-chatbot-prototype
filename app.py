from dotenv import load_dotenv
import os
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_community.utilities import SQLDatabase
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
import gradio as gr
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain.agents.agent_types import AgentType
import sqlite3

# Load environment variables from config.env file
load_dotenv(dotenv_path='config.env')

# Set OpenAI API key with a fallback (NOT RECOMMENDED FOR PRODUCTION)
openai_api_key = os.getenv("OPENAI_API_KEY")

def init_database(database: str) -> SQLDatabase:
    db_uri = f"sqlite:///{database}.db"
    sql_db = SQLDatabase.from_uri(db_uri)
    
    # Create sample tables and insert data if they don't exist
    conn = sqlite3.connect(f"{database}.db")
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS customers (
                        customerNumber INTEGER PRIMARY KEY,
                        customerName TEXT,
                        contactLastName TEXT,
                        contactFirstName TEXT,
                        phone TEXT,
                        addressLine1 TEXT,
                        addressLine2 TEXT,
                        city TEXT,
                        state TEXT,
                        postalCode TEXT,
                        country TEXT,
                        salesRepEmployeeNumber INTEGER,
                        creditLimit REAL
                    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS employees (
                        employeeNumber INTEGER PRIMARY KEY,
                        lastName TEXT,
                        firstName TEXT,
                        extension TEXT,
                        email TEXT,
                        officeCode TEXT,
                        reportsTo INTEGER,
                        jobTitle TEXT
                    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS offices (
                        officeCode TEXT PRIMARY KEY,
                        city TEXT,
                        phone TEXT,
                        addressLine1 TEXT,
                        addressLine2 TEXT,
                        state TEXT,
                        country TEXT,
                        postalCode TEXT,
                        territory TEXT
                    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS orderdetails (
                        orderNumber INTEGER,
                        productCode TEXT,
                        quantityOrdered INTEGER,
                        priceEach REAL,
                        orderLineNumber INTEGER,
                        PRIMARY KEY (orderNumber, productCode)
                    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
                        orderNumber INTEGER PRIMARY KEY,
                        orderDate TEXT,
                        requiredDate TEXT,
                        shippedDate TEXT,
                        status TEXT,
                        comments TEXT,
                        customerNumber INTEGER
                    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS payments (
                        customerNumber INTEGER,
                        checkNumber TEXT,
                        paymentDate TEXT,
                        amount REAL,
                        PRIMARY KEY (customerNumber, checkNumber)
                    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS productlines (
                        productLine TEXT PRIMARY KEY,
                        textDescription TEXT,
                        htmlDescription TEXT,
                        image BLOB
                    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS products (
                        productCode TEXT PRIMARY KEY,
                        productName TEXT,
                        productLine TEXT,
                        productScale TEXT,
                        productVendor TEXT,
                        productDescription TEXT,
                        quantityInStock INTEGER,
                        buyPrice REAL,
                        MSRP REAL
                    )''')
    
    # Insert sample data if tables are empty
    cursor.execute("SELECT COUNT(*) FROM customers")
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''INSERT INTO customers VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', [
            (103, 'Atelier graphique', 'Schmitt', 'Carine', '40.32.2555', '54, rue Royale', None, 'Nantes', None, '44000', 'France', 1370, 21000.00),
            (112, 'Signal Gift Stores', 'King', 'Jean', '7025551838', '8489 Strong St.', None, 'Las Vegas', 'NV', '83030', 'USA', 1166, 71800.00)
        ])
    
    conn.commit()
    conn.close()
    
    return sql_db

class SQLAgent:
    def __init__(self, db: SQLDatabase, openai_api_key: str):
        self.db = db
        self.llm = ChatOpenAI(temperature=0, model="gpt-4o", openai_api_key=openai_api_key)
        self.toolkit = SQLDatabaseToolkit(db=self.db, llm=self.llm)
        self.agent = create_sql_agent(
            llm=self.llm,
            toolkit=self.toolkit,
            agent_type=AgentType.OPENAI_FUNCTIONS,
            verbose=True,
            max_iterations=5,
        )

    def run(self, query: str):
        try:
            result = self.agent.run(query)
            return result
        except Exception as e:
            return f"An error occurred: {str(e)}"

class ChatBot:
    def __init__(self):
        self.db = None
        self.chat_history = []
        self.agent = None

    def connect_to_database(self, database):
        try:
            self.db = init_database(database)
            self.agent = SQLAgent(self.db, openai_api_key)
            return "Connected to database successfully!"
        except Exception as e:
            return f"Failed to connect to database: {str(e)}"

    def chat(self, user_message):
        if not self.db or not self.agent:
            return "Please connect to a database first."
        
        self.chat_history.append(HumanMessage(content=user_message))
        ai_message = get_response(user_message, self.agent, self.chat_history)
        self.chat_history.append(AIMessage(content=ai_message))
        
        return ai_message

def get_response(user_query: str, agent: SQLAgent, chat_history: list):
    # Use the agent to get the response
    agent_response = agent.run(user_query)
    
    # Format the response
    template = """
    You are a data analyst at a company. You are interacting with a user who is asking questions about the company's database.
    Based on the agent's response, write a natural language response.

    Conversation History: {chat_history}
    User question: {question}
    Agent Response: {response}"""
    
    prompt = ChatPromptTemplate.from_template(template)
    llm = ChatOpenAI(model="gpt-4o", temperature=0, api_key=openai_api_key)
    
    chain = (
        prompt
        | llm
        | StrOutputParser()
    )
    
    return chain.invoke({
        "question": user_query,
        "chat_history": chat_history,
        "response": agent_response
    })

# Creating an instance of ChatBot
chat_bot = ChatBot()

def user(user_message, history):   
    return "", history + [[user_message, None]]

def bot(history):
    user_message = history[-1][0]
    bot_message = chat_bot.chat(user_message)
    history[-1][1] = bot_message
    return history

with gr.Blocks() as demo:
    # Display the title of the application
    gr.Markdown("# SQL")
    
    # Create an input for the database name and a connect button in a row
    with gr.Row():
        database_input = gr.Textbox(label="Database Name", placeholder="Enter database name")
        connect_button = gr.Button("Connect")
    
    # Textbox for displaying the connection status, not interactive
    connection_status = gr.Textbox(label="Connection Status", interactive=False)
    
    # Chatbot component to display the conversation
    chatbot = gr.Chatbot([], elem_id="chatbot", height=350)
    
    # Textbox for user to type their message
    msg = gr.Textbox(label="Type your message here")
    
    # Clear button to reset the chatbot and message input
    clear = gr.ClearButton([msg, chatbot])

    # Connect the connect button to the `connect_to_database` method
    connect_button.click(chat_bot.connect_to_database, inputs=[database_input], outputs=[connection_status])
   
    # Chain events where message submission triggers user function followed by bot function
    msg.submit(user, [msg, chatbot], [msg, chatbot], queue=False).then(
        bot, chatbot, chatbot
    )

if __name__ == "__main__":
    # Launch the Gradio interface
    demo.launch(share=True)
