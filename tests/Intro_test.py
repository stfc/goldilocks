import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/qe_input')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/qe_input/pages')))

from streamlit.testing.v1 import AppTest
import pytest
import json

from dotenv import load_dotenv
from pymatgen.core.structure import Structure


load_dotenv()
mp_api_key = os.getenv("MP_API_KEY")

CIF="""# generated using pymatgen
data_CoF2
_symmetry_space_group_name_H-M   'P 1'
_cell_length_a   4.64351941
_cell_length_b   4.64351941
_cell_length_c   3.19916469
_cell_angle_alpha   90.00000000
_cell_angle_beta   90.00000000
_cell_angle_gamma   90.00000000
_symmetry_Int_Tables_number   1
_chemical_formula_structural   CoF2
_chemical_formula_sum   'Co2 F4'
_cell_volume   68.98126085
_cell_formula_units_Z   2
loop_
 _symmetry_equiv_pos_site_id
 _symmetry_equiv_pos_as_xyz
  1  'x, y, z'
loop_
 _atom_type_symbol
 _atom_type_oxidation_number
  Co2+  2.0
  F-  -1.0
loop_
 _atom_site_type_symbol
 _atom_site_label
 _atom_site_symmetry_multiplicity
 _atom_site_fract_x
 _atom_site_fract_y
 _atom_site_fract_z
 _atom_site_occupancy
  Co2+  Co0  1  0.00000000  0.00000000  0.00000000  1
  Co2+  Co1  1  0.50000000  0.50000000  0.50000000  1
  F-  F2  1  0.30433674  0.30433674  0.00000000  1
  F-  F3  1  0.69566326  0.69566326  0.00000000  1
  F-  F4  1  0.80433674  0.19566326  0.50000000  1
  F-  F5  1  0.19566326  0.80433674  0.50000000  1"""

ELEMENTS=['Ac', 'Ag', 'Al', 'Am', 'Ar', 'As', 'At', 'Au', 'B', 'Ba', 'Be',\
       'Bi', 'Bk', 'Br', 'C', 'Ca', 'Cd', 'Ce', 'Cf', 'Cl', 'Cm', 'Co',\
       'Cr', 'Cs', 'Cu', 'Dy', 'Er', 'Es', 'Eu', 'F', 'Fe', 'Fm', 'Fr',\
       'Ga', 'Gd', 'Ge', 'H', 'He', 'Hf', 'Hg', 'Ho', 'I', 'In', 'Ir',\
       'K', 'Kr', 'La', 'Li', 'Lr', 'Lu', 'Md', 'Mg', 'Mn', 'Mo', 'N',\
       'Na', 'Nb', 'Nd', 'Ne', 'Ni', 'No', 'Np', 'O', 'Os', 'P', 'Pa',\
       'Pb', 'Pd', 'Pm', 'Po', 'Pr', 'Pt', 'Pu', 'Ra', 'Rb', 'Re', 'Rh',\
       'Rn', 'Ru', 'S', 'Sb', 'Sc', 'Se', 'Si', 'Sm', 'Sn', 'Sr', 'Ta',\
       'Tb', 'Tc', 'Te', 'Th', 'Ti', 'Tl', 'Tm', 'U', 'V', 'W', 'Xe', 'Y',\
       'Yb', 'Zn', 'Zr']

@pytest.fixture
def formula():
    return 'SiO2'

def test_info_input_page(formula):
    at = AppTest.from_file("src/qe_input/pages/Intro.py")
    at.run()
    assert not at.exception
    for x in at.get('selectbox'):
        if(x.label=='XC-functional'):
            assert 'PBE' in x.options
            assert 'PBEsol' in x.options
            x._value='PBEsol'
            x.run()
            assert at.session_state['functional']=='PBEsol'
        if(x.label=='pseudopotential flavour'):
            assert 'efficiency' in x.options
            assert 'precision' in x.options
            x._value='precision'
            x.run()
            assert at.session_state['mode']=='precision'
    for x in at.get('text_input'):
        if(x.label=="Chemical formula (try to find structure in free databases)"):
            x._value=formula
            x.run()
            for x in at.get('radio'):
                assert 'Jarvis' in x.options
                assert 'MP' in x.options
                assert 'MC3D' in x.options
                assert 'OQMD' in x.options
            assert isinstance(at.session_state['structure'], Structure)

def test_structure_read(tmp_path):
    mock_file = tmp_path / 'mock_structure.cif'
    mock_file.write_text(CIF, encoding="utf-8")
    assert Structure.from_file(mock_file)
    assert Structure.from_file(mock_file).lattice
    assert Structure.from_file(mock_file).formula
    # try to open corrupted cif
    with pytest.raises(ValueError):
        mock_file = tmp_path / 'mock_structure.cif'
        mock_file.write_text(CIF[-10], encoding="utf-8")
        assert Structure.from_file(mock_file)

def test_pseudos():
    assert os.path.exists('./src/qe_input/pseudos/')
    assert os.path.exists('./src/qe_input/pseudo_cutoffs/')
    list_of_pseudo_types=os.listdir('./src/qe_input/pseudos/')
    list_of_pseudo_types.remove(".DS_Store")
    list_of_cutoffs=os.listdir('./src/qe_input/pseudo_cutoffs/')
    list_of_cutoffs.remove(".DS_Store")

    # check that for each combination of functional and mode there is a folder
    # that each folder contains psudos for all elements
    at = AppTest.from_file("src/qe_input/pages/Intro.py")
    at.run()
    for x in at.get('selectbox'):
        if(x.label=='XC-functional'):
            functional_options=x.options
        if(x.label=='pseudopotential flavour'):
            mode_options=x.options
    for functional in functional_options:
        for mode in mode_options:
            switch_pseudo=0
            switch_cutoff=0
            for pseudo in list_of_pseudo_types:
                if(functional in pseudo and mode in pseudo):
                    switch_pseudo=1
            for cutoff_name in list_of_cutoffs:
                if(functional in pseudo and mode in cutoff_name):
                    switch_cutoff=1
            assert switch_pseudo # it would be good to add a message about what functional/mode combination fail
            assert switch_cutoff
    for folder in list_of_pseudo_types:
        list_of_files=os.listdir('./src/qe_input/pseudos/'+folder)
        represented_elements=[]
        for file in list_of_files:
            if(file[1]=='.' or file[1]=='_' or file[1]=='-'):
                el=file[0]
                el=el.upper()
            elif(file[2]=='.' or file[2]=='_' or file[2]=='-'):
                el=file[:2]
                el=el[0].upper()+el[1].lower()
            assert el in ELEMENTS
            represented_elements.append(el)
        for el in ELEMENTS:
            assert el in represented_elements
    for file in list_of_cutoffs:
        with open('./src/qe_input/pseudo_cutoffs/'+file,'r') as f:
            cutoffs=json.load(f)
            for el in ELEMENTS:
                assert el in cutoffs.keys()