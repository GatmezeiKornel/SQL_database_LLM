import tiktoken
import openai
import streamlit as st
from utils.streamlit_functions import *
from utils.prompts.prompt import *
from utils.prompts.Schema_Prompt_v1 import *

encoding = tiktoken.get_encoding("cl100k_base")
MODEL = 'gpt-4-turbo-2024-04-09'
MODEL_INPUT_TOKEN_SUMM_LIMIT = 125000
MODEL_MAX_TOKEN_LIMIT = 128000
MAX_TOKENS = MODEL_MAX_TOKEN_LIMIT-MODEL_INPUT_TOKEN_SUMM_LIMIT
MAX_CONTEXT_QUESTIONS = 120
TEMPERATURE = 0

def generate_response(messages, MODEL, TEMPERATURE, MAX_TOKENS):
    completion = openai.ChatCompletion.create(
        model=MODEL, 
        messages=messages, 
        temperature=TEMPERATURE, 
        max_tokens=MAX_TOKENS)
    return completion.choices[0]['message']['content']



def app_main():
    set_config()
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated and not check_password():
        st.stop()
    else:
        st.session_state.authenticated = True

    # - - - - - - - - - - - - - - - -
    # Chat section
    # - - - - - - - - - - - - - - - -
    
     # Set a default model
    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = MODEL

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
   
    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if QUERY := st.chat_input("Ide írja a kérdését"):
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(QUERY)
        with st.chat_message("assistant"):
            message_placeholder = st.empty()

            sql_gen_messages = [
                {"role": "system", "content" : sql_system_message.format(system_prompt=SQL_SYSTEM_PROMPT, 
                                                                    table_info=SCHEMA_PROMPT, 
                                                                    few_shot_examples=FEW_SHOT_EXAMPLES_SQL)},
                {"role": "user", "content": question_message.format(question=QUERY)}
                ]

            sql_response = generate_response(sql_gen_messages, MODEL, TEMPERATURE, MAX_TOKENS)

            messages = [
                {"role": "system", "content" : text_system_message.format(system_prompt=DB_TO_TEXT_SYSTEM_PROMPT, 
                                                                    sql_data=sql_response)},
                *st.session_state.messages,
                {"role": "user", "content": question_message.format(question=QUERY)}
            ]

            text_response = generate_response(sql_gen_messages, MODEL, TEMPERATURE, MAX_TOKENS)

            current_token_count = len(encoding.encode(' '.join([i['content'] for i in messages])))

            while (len(messages)-3 > MAX_CONTEXT_QUESTIONS[MODEL] * 2) or (current_token_count >= MODEL_INPUT_TOKEN_SUMM_LIMIT[MODEL]):

                messages.pop(3)            
                current_token_count = len(encoding.encode(' '.join([i['content'] for i in messages])))


            message_placeholder.markdown(text_response)

        # Add user and AI message to chat history
        st.session_state.messages.append({"role": "user", "content": QUERY})
        st.session_state.messages.append({"role": "assistant", "content": text_response})

if __name__ == "__main__":
    app_main()