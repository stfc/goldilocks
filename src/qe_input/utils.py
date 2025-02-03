import os
import shutil
import re
import json
from pymatgen.core.composition import Composition
import numpy as np
from typing import Dict
import streamlit as st
from pathlib import Path
import math

def list_of_pseudos(pseudo_potentials_folder: str, 
                    functional: str,
                    mode: str, 
                    compound: str,
                    target_folder: str) -> tuple:
    '''
    Function to determine the list of names of files with pseudopotentials for the compound
    Args:
        pseudo_potentials_folder: str, name of the parent forlder with pseudopotentials
        functional: str, name of the DFT functional
        mode: str, mode for pseudopotential, list of possible values: ["efficiency", "precision"]
        compound: str, composition of the compound
    '''
    list_of_subfolders=os.listdir(pseudo_potentials_folder)
    for subfolder in list_of_subfolders:
        if(re.search(functional.lower()+"_", subfolder.lower()) and re.search(mode.lower(), subfolder.lower())):
            list_of_files=os.listdir(pseudo_potentials_folder+subfolder+"/")
            chosen_subfolder=subfolder
    #print('The list of pseudo files is: ', list_of_files[0], ', ...')
    #print(list_of_files)
    list_of_element_files={}
    for file in list_of_files:
        for element in Composition(compound).elements:
            element=str(element)
            if(file[:len(element)].lower()==element.lower() and not file[len(element):len(element)+1].lower().isalpha()):
                list_of_element_files[element]=file
                shutil.copyfile(pseudo_potentials_folder+chosen_subfolder+"/"+file, target_folder+file)
                
    return chosen_subfolder, list_of_element_files

def cutoff_limits(pseudo_potentials_cutoffs_folder: str, 
                  functional: str,
                  mode: str,
                  compound: str) -> Dict:
    '''
    Function to determine the maximum energy cutoff and density cutoff possible based on cutoff values specified for pseudopotentials
    Args:
        pseudo_potentials_cutoffs: str, the main folder with pseudopotential cutoffs
        functional: str, name of the DFT functional
        mode: str, mode for pseudopotential, list of possible values: ["efficiency", "precision"]
        compound: str, composition of the compound
    Output:
        Dictionary with keys 'max_ecutwfc' and 'max_ecutrho' and float values
    '''
    list_of_cutoff_files=os.listdir(pseudo_potentials_cutoffs_folder)
    for file in list_of_cutoff_files:
        if(re.search(functional.lower()+"_", file.lower()) and re.search(mode.lower(), file.lower())):
            try:
                with open(pseudo_potentials_cutoffs_folder+file, "r") as f:
                    cutoffs=json.load(f)
            except FileNotFoundError:
                cutoffs={}
    elements=[str(el) for el in Composition(compound).elements]
    if(cutoffs!={}):
        subset={key:cutoffs[key] for key in elements}
        encutoffs=[subset[i]['cutoff_wfc'] for i in subset.keys()]
        rhocutoffs=[subset[i]['cutoff_rho'] for i in subset.keys()]
        max_ecutoff=max(encutoffs)
        max_rhocutoff=max(rhocutoffs)
    else:
        max_ecutoff=np.nan
        max_rhocutoff=np.nan
    return { 'max_ecutwfc': max_ecutoff, 'max_ecutrho': max_rhocutoff}

def generate_input_file(save_directory, structure_file, pseudo_path_temp, dict_pseudo_file_names, max_ecutwfc, max_ecutrho, kspacing):
    """
    This function generates the input file for Quantum Espresso for single point energy scf calculations.
    It save the file on disk and prints it out.
    Arguments: generator input of type PW_input_data
    """

    from ase.io.espresso import write_espresso_in
    from pymatgen.core.structure import Structure
    from pymatgen.io.ase import AseAtomsAdaptor
    
    pymatgen_structure=Structure.from_file(structure_file)
    adaptor = AseAtomsAdaptor()
    structure = adaptor.get_atoms(pymatgen_structure)

    input_data = {
        'calculation': 'scf',
        'restart_mode': 'from_scratch',
        'tprnfor': True,
        'etot_conv_thr': 1e-5,
        'forc_conv_thr': 1e-4,
        'ecutwfc': int(max_ecutwfc),
        'ecutrho': int(max_ecutrho),
        'occupations': 'smearing',
        'degauss': 0.0045,
        'smearing': 'fermi-dirac',
        'conv_thr': 1e-8,
        'mixing_mode': 'plain',
        'mixing_beta': 0.6,
        'diagonalization': 'ppcg',
        'startingwfc':'atomic+random'
    }
    save_directory = Path(save_directory)
    filename = save_directory / 'qe.in'
    write_espresso_in(str(filename), structure, input_data=input_data, pseudopotentials=dict_pseudo_file_names, 
                      kspacing=float(kspacing), format='espresso-in')
    input_file_content=''
    with open(str(filename),'r') as file:
        for line in file:
            input_file_content+=line
            if('&CONTROL' in line):
                indent=3
                key='pseudo_dir'
                value=pseudo_path_temp
                input_file_content+=f"{' ' * indent}{key:16} = '{value}'\n"
    with open(str(filename),'w') as file:
        file.write(input_file_content)
    input_file_content=input_file_content[:-1]
    return input_file_content

def update_input_file(file_path: str, new_content: str) -> None:
    """The function to update the content of input file
       Input: file_path the location of the file to be update
              new_content new content to write in the file
    """
    with open(file_path,'w') as file:
       file.write(new_content)
    st.write('qe.in file was updated')
    return

def atomic_positions_list(structure):
    string=""
    for site in structure.sites:
        string+=site.as_dict()['species'][0]['element']+' '+str(site.coords[0])+\
        ' '+str(site.coords[1])+' '+str(site.coords[2])+'\n'
    return string

def generate_kpoints_grid(structure, kspacing):
    kpoints = [math.ceil(1/x/kspacing) for x in structure.lattice.abc]
    kpoints.extend([0,0,0])
    return kpoints

def generate_response(messages,client,llm_model):
    """Generator function to stream response from Groq API"""
    response = client.chat.completions.create(
        model=llm_model,  # Example model, change as needed
        messages=messages,
        stream=True  # Enable streaming
    )

    for chunk in response:
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content