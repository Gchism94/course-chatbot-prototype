from langdetect import detect
from transformers import pipeline
import gradio as gr

# Load models
print("Loading models... This may take a while.")
flan_model = pipeline("text2text-generation", model="google/flan-t5-base")
bloom_model = pipeline("text-generation", model="bigscience/bloomz")
llama_model = pipeline("text-generation", model="meta-llama/LLaMA-2-7b")
print("Models loaded successfully!")

# Function to detect language
def detect_language(query):
    try:
        return detect(query)
    except Exception as e:
        return "unknown"

# Function to select model
def select_model(query):
    language = detect_language(query)
    
    if language != "en":
        return "bloom"  # Use BLOOM for non-English queries
    elif "code" in query.lower() or "programming" in query.lower():
        return "bloom"  # Use BLOOM for programming-related queries
    elif "explain" in query.lower() or "what is" in query.lower():
        return "flan-t5"  # Use FLAN-T5 for instructional queries
    else:
        return "llama"  # Use LLaMA for deep contextual or general queries

# Function to generate response
def generate_response(query, model_name):
    if model_name == "flan-t5":
        return flan_model(query)[0]['generated_text']
    elif model_name == "bloom":
        return bloom_model(query, max_length=200)[0]['generated_text']
    elif model_name == "llama":
        return llama_model(query, max_length=200)[0]['generated_text']
    else:
        return "Error: Invalid model selected."

# Chatbot logic
def chatbot_response(user_query):
    model_name = select_model(user_query)  # Select the appropriate model
    response = generate_response(user_query, model_name)  # Generate response
    return f"**Model used**: {model_name}\n\n**Response**: {response}"

# Gradio interface
with gr.Interface(
    fn=chatbot_response, 
    inputs=gr.Textbox(label="Enter your question"), 
    outputs=gr.Textbox(label="Chatbot Response"), 
    title="Dynamic Model Selection Chatbot",
    description=(
        "This chatbot dynamically selects the most suitable model (LLaMA, BLOOM, or FLAN-T5) "
        "based on your query. It supports multilingual, programming, and instructional tasks."
    )
) as demo:
    demo.launch(share=True)