import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/qe_input')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/qe_input/pages')))

from streamlit.testing.v1 import AppTest
import streamlit as st

from dotenv import load_dotenv


load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
groq_api_key = os.getenv("GROQ_API_KEY")


def test_chatbot_openai_page():
    at = AppTest.from_file("src/qe_input/QE_input.py")
    at.run()
    at.switch_page("pages/Chatbot_generator.py")
    at.run()
    assert not at.exception
    for x in at.sidebar.get('selectbox'):
        if(x.label=='assistant LLM'):
            assert 'gpt-4o' in x.options
            assert 'gpt-4o-mini' in x.options
            assert 'gpt-3.5-turbo' in x.options
            x._value='gpt-3.5-turbo'
            x.run()
            assert at.session_state['llm_name']=='gpt-3.5-turbo'
            at.sidebar.get('text_input')[0]._value=openai_api_key
            at.run()
            assert at.session_state['openai_api_key'] == openai_api_key
            assert at.get('chat_input')!=[]
            assert at.session_state['messages']==[]
            at.get('chat_input')[0].set_value('Hello')
            at.get('chat_input')[0].run()
            assert at.session_state['messages']!=[] 
            assert at.session_state['messages'][0]['role']=='system'
            assert at.session_state['messages'][1]['role']=='user'
            assert at.session_state['messages'][2]['role']=='assistant'

def test_chatbot_groq_page():
    at = AppTest.from_file("src/qe_input/QE_input.py")
    at.run()
    at.switch_page("pages/Chatbot_generator.py")
    at.run()
    assert not at.exception
    for x in at.sidebar.get('selectbox'):
        if(x.label=='assistant LLM'):
            assert 'llama-3.3-70b-versatile' in x.options
            x._value='llama-3.3-70b-versatile'
            x.run()
            assert at.session_state['llm_name']=='llama-3.3-70b-versatile'
            at.sidebar.get('text_input')[0]._value=groq_api_key
            at.run()
            assert at.session_state['groq_api_key'] == groq_api_key
            assert at.get('chat_input')!=[]
            assert at.session_state['messages']==[]
            at.get('chat_input')[0].set_value('Hello')
            at.get('chat_input')[0].run()
            assert at.session_state['messages']!=[] 
            assert at.session_state['messages'][0]['role']=='system'
            assert at.session_state['messages'][1]['role']=='user'
            assert at.session_state['messages'][2]['role']=='assistant'