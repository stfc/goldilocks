import os
import streamlit as st
import shutil
from pymatgen.core.structure import Structure
from pymatgen.core.composition import Composition
from pymatgen.io.cif import CifWriter
from utils import list_of_pseudos, cutoff_limits
from data_utils import jarvis_structure_lookup, mp_structure_lookup, mc3d_structure_lookup, oqmd_strucutre_lookup
from kspacing_model import predict_kspacing


st.write("# Welcome to QE input generator! 👋")

st.markdown("""This app will help you generate input files for Quantum Espresso calculations.""")

st.sidebar.success("Provide specifications and select a way to generate input")

st.session_state['all_info']=False
structure=None

col1, col2 =st.columns(2)

with col1:
    functional_value = st.selectbox('XC-functional', 
                                ('PBE','PBEsol'), 
                                index=None, 
                                placeholder='PBE')

with col2:
    mode_value = st.selectbox('pseudopotential flavour', 
                            ('efficiency','precision'), 
                            index=None, 
                            placeholder='efficiency')

if functional_value:
    st.session_state['functional'] = functional_value
else:
    st.session_state['functional'] = 'PBE'

if mode_value:
    st.session_state['mode'] = mode_value
else:
    st.session_state['mode'] = 'efficiency'


# upload structure file into buffer
tab1, tab2 = st.tabs(["Upload structure", "Search for structure"])

with tab1:
    structure_file = st.file_uploader("Upload the structure file", type=("cif"))

with tab2:
    input_formula = st.text_input("Chemical formula (try to find structure in free databases)")

if not structure_file and not input_formula:
    st.info("Please add your structure file or chemical formula to continue")
elif input_formula:
    composition=Composition(input_formula)
    formula,_=composition.get_reduced_formula_and_factor()
    # may also include alexandria https://alexandria.icams.rub.de/
    structure_database = st.radio(label='Choose the database to search for the structure',
                                  options=['Jarvis','MP', 'MC3D', 'OQMD'],
                                  horizontal=True,
                                  )
    if structure_database=='Jarvis':
        try:
            structure=jarvis_structure_lookup(formula)
            st.info('Structure was found in Jarvis 3d_dft dataset')
        except:
            st.info('Structure was not found!')
    elif structure_database=='MP':
        mp_api_key = st.text_input("Materials Project API Key ([Get a MP API key](https://next-gen.materialsproject.org/api#api-key))", key="mp_api_key", type="password")
        if mp_api_key:
            try:
                structure=mp_structure_lookup(formula,mp_api_key)
                st.info('Structure was found in Materials Project database')
            except:
                st.info('Structure was not found!')
    elif structure_database=='MC3D':
        try:
            structure=mc3d_structure_lookup(formula)
            st.info('Structure was found in MC3D dataset')
        except Exception as exc:
            st.info('Structure was not found!')
            # st.info(exc)
    elif structure_database=='OQMD':
        try:
            structure=oqmd_strucutre_lookup(formula)
            st.info('Structure was found in OQMD database')
        except Exception as exc:
            st.info('Structure was not found!')
            # st.info(exc)
elif structure_file:
    save_directory = "./src/qe_input/temp/"
    if os.path.exists(save_directory):
        shutil.rmtree(save_directory, ignore_errors=True)
    os.makedirs(save_directory)
    file_path = os.path.join(save_directory, 'structure.cif')
    with open(file_path, "wb") as f:
        f.write(structure_file.getbuffer())
    structure = Structure.from_file(file_path)

if structure:
    save_directory = "./src/qe_input/temp/"
    if os.path.exists(save_directory):
        shutil.rmtree(save_directory, ignore_errors=True)
    os.makedirs(save_directory)
    file_path = os.path.join(save_directory, 'structure.cif')
    write_cif=CifWriter(structure)
    write_cif.write_file(file_path)
    st.session_state['save_directory']=save_directory
    st.session_state['structure_file']=file_path
    st.session_state['structure']=structure

    composition = Composition(structure.alphabetical_formula)
    st.session_state['composition']=structure.alphabetical_formula
    pseudo_path="./src/qe_input/pseudos/"
    pseudo_family, list_of_element_files=list_of_pseudos(pseudo_path, st.session_state['functional'], 
                                                         st.session_state['mode'], composition,st.session_state['save_directory'])
    st.session_state['pseudo_family']=pseudo_family
    st.session_state['list_of_element_files']=list_of_element_files
    st.session_state['pseudo_path']=pseudo_path

    cutoffs=cutoff_limits('./src/qe_input/pseudo_cutoffs/', st.session_state['functional'],
                          st.session_state['mode'], composition)
    st.session_state['cutoffs']=cutoffs
    kspacing=predict_kspacing(structure)
    st.session_state['kspacing']=kspacing

    st.session_state['all_info']=True
