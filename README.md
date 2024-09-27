# SQL Agentic RAG Chatbot

## Demo

See the SQL Agentic RAG Chatbot in action:

![Demo Video](https://github.com/naman1618/sql_agentic_rag_chatbot/blob/main/sql_rag-ezgif.com-video-to-gif-converter.gif)

## Overview

SQL Agentic RAG Chatbot is an advanced, AI-powered interface for interacting with SQL databases using natural language. This innovative tool combines the power of Language Models (LLMs) with Retrieval-Augmented Generation (RAG) to provide an intuitive, conversational approach to database querying and analysis.

## Features

- **Natural Language Queries**: Ask questions about your database in plain English.
- **SQL Query Generation**: Automatically generates SQL queries based on natural language input.
- **Intelligent Response Synthesis**: Provides answers in natural language, explaining the results clearly.
- **Multi-Table Support**: Capable of handling complex queries across multiple related tables.
- **RAG-Enhanced Responses**: Utilizes Retrieval-Augmented Generation for more accurate and context-aware answers.
- **User-Friendly Interface**: Built with Gradio for an intuitive, web-based interaction.
- **Flexible Database Support**: Can connect to and interact with any SQL database, making it highly versatile.

## How It Works

1. **User Input**: The user submits a question in natural language about the database.
2. **Query Processing**: The LLM-powered agent interprets the question and formulates an appropriate SQL query.
3. **Database Interaction**: The generated SQL query is executed against the connected database.
4. **Result Interpretation**: The raw SQL results are processed and interpreted by the AI.
5. **Natural Language Response**: A human-readable answer is generated, explaining the query results in context.

This demo showcases:
- Connecting to a sample database
- Asking complex questions in natural language
- Viewing the AI-generated SQL queries
- Receiving detailed, context-aware answers

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/naman1618/sql_agentic_rag_chatbot.git
   cd sql_agentic_rag_chatbot
   ```

2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your OpenAI API key in a `.env` file:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

## Usage

1. Run the chatbot:
   ```bash
   python src/chatbot.py
   ```

2. Open the provided Gradio interface URL in your web browser.
3. Enter the name or connection details of your SQL database and click "Connect".
4. Start asking questions about your data in natural language!

## Example Queries

- "How many customers do we have in each country?"
- "What's the total revenue from orders in the last quarter?"
- "Who are our top 5 customers by sales volume?"
- "Show me the product categories with the highest profit margins."

## Technical Details

- **LLM**: Utilizes OpenAI's GPT model for natural language understanding and generation.
- **RAG Implementation**: Enhances responses by retrieving relevant context from the database schema and previous interactions.
- **SQL Agent**: Custom-built agent using LangChain for dynamic SQL query construction.
- **Database**: Supports any SQL database, including but not limited to PostgreSQL, MySQL, SQL Server, and Oracle. SQLite is used for testing purposes, but the architecture is designed for flexibility.

## Limitations and Future Work

- While optimized for general SQL databases, the chatbot's performance may vary with extremely large datasets or complex schema.
- Ongoing work is being done to improve query optimization and handling of edge cases in natural language interpretation.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- OpenAI for their GPT model
- LangChain for the excellent tools and frameworks
- The open-source community for invaluable resources and inspiration
