import os
import streamlit as st
import pandas as pd
from openai import OpenAI
from groq import Groq
from utils import atomic_positions_list, generate_kpoints_grid, generate_response

st.title("Generate QE input with an LLM Agent")

groq_api_key=None
openai_api_key=None

if 'all_info' not in st.session_state.keys():
    st.session_state['all_info']=False

with st.sidebar:
    llm_name_value = st.selectbox('assistant LLM', 
                        ("gpt-4o", "gpt-4o-mini", 'gpt-3.5-turbo', 'llama-3.3-70b-versatile'), 
                        index=None, 
                        placeholder='gpt-4o-mini')

    if llm_name_value in ["gpt-4o", "gpt-4o-mini", 'gpt-3.5-turbo']:
        openai_api_key = st.text_input("OpenAI API Key ([Get an OpenAI API key](https://platform.openai.com/account/api-keys))", 
                                    key="openai_api_key", 
                                    type="password",
                                    )
    elif llm_name_value in ['llama-3.3-70b-versatile']:
        groq_api_key = st.text_input("Groq API Key ([Get an Groq API key](https://console.groq.com/keys))", 
                                   key="groq_api_key", 
                                   type="password",
                                   )
    if llm_name_value in ['llama-3.3-70b-versatile']:
        st.session_state['llm_name'] = llm_name_value
    else:
        st.session_state['llm_name'] = 'gpt-4o'

    if not openai_api_key:
        if llm_name_value in ["gpt-4o", "gpt-4o-mini", 'gpt-3.5-turbo']:
            st.info("Please add your OpenAI API key to continue.", icon="🗝️")

    if not groq_api_key:
        if llm_name_value in ['llama-3.3-70b-versatile']:
            st.info("Please add your Groq API key to continue.", icon="🗝️")

if not (st.session_state['all_info']):
    st.info("Please provide all necessary material information on the Intro page")


if (openai_api_key or groq_api_key) and st.session_state['all_info']:
    # Create an OpenAI client.
    if llm_name_value in ["gpt-4o", "gpt-4o-mini", 'gpt-3.5-turbo']:
        client = OpenAI(api_key=openai_api_key)
    elif llm_name_value in ['llama-3.3-70b-versatile']:
        client = Groq(api_key=groq_api_key)

    st.markdown('** Ask the agent to generate an input QE SCF file for the compound you uploaded**')
    # Create a session state variable to store the chat messages. This ensures that the
    # messages persist across reruns.

    cell_params=st.session_state['structure'].lattice.matrix

    atomic_positions=atomic_positions_list(st.session_state['structure'])
    kpoints=generate_kpoints_grid(st.session_state['structure'], st.session_state['kspacing'])

    task=f"You are the assitant for generation input file for single point \
              energy calculations with Quantum Espresso. If the user asks to generate an input file, \
              the following information is availible to you: \
              the formula of the compound {st.session_state['composition']},\
              the list of pseudo potential files {st.session_state['list_of_element_files']},\
              the path to pseudo potential files './',\
              the cell parameters in angstroms {cell_params},\
              the atomic positions in angstroms {atomic_positions},\
              the energy cutoff is {st.session_state['cutoffs'][ 'max_ecutwfc']} in Ry,\
              the density cutoff is {st.session_state['cutoffs'][ 'max_ecutrho']} in Ry,\
              kpoints automatic are {kpoints}. \
              Please calculate forces, and do gaussian smearing for dielectrics and semiconductors \
              smearing for metals. Try to assess whether the provided compound is \
              metal, dielectric or semiconductor before generation"
    

    if "messages" not in st.session_state:
        st.session_state.messages=[{"role": "system", "content": task}]
    else:
        for message in st.session_state.messages:
            if message['role']=='system':
                message['content']=task

    for message in st.session_state.messages:
        if(message["role"]=="user" or message["role"]=="assistant"):
            st.markdown(message["content"])


    if prompt := st.chat_input("Do you have any questions?"):

        # Store and display the current prompt.
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate a response using the OpenAI API.
        if st.session_state['llm_name'] in ["gpt-4o", "gpt-4o-mini", 'gpt-3.5-turbo']:
            stream = client.chat.completions.create(
                model=st.session_state['llm_name'],
                messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                stream=True,
            )
        elif st.session_state['llm_name'] in ['llama-3.3-70b-versatile']:
            stream = generate_response(messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                                       client=client,
                                       llm_model=st.session_state['llm_name'])

        # Stream the response to the chat using `st.write_stream`, then store it in 
        # session state.
        with st.chat_message("assistant"):
            response = st.write(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})