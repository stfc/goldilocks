import sys
import os
from streamlit.testing.v1 import AppTest
from pymatgen.core.structure import Structure
import json
import pandas as pd
from io import BytesIO
from unittest.mock import patch
import pytest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/qe_input')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/qe_input/pages')))

@pytest.fixture
def sample_cif():
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
    return BytesIO(CIF.encode("utf-8"))
@pytest.fixture
def ELEMENTS():
    return ['Ac', 'Ag', 'Al', 'Am', 'Ar', 'As', 'At', 'Au', 'B', 'Ba', 'Be',\
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

@pytest.fixture
def sample_structure():
    """Create a sample structure for testing"""
    # Create a simple SiO2 structure
    lattice = [[5, 0, 0], [0, 5, 0], [0, 0, 5]]
    species = ['Si', 'O', 'O']
    coords = [[0, 0, 0], [0.5, 0.5, 0.5], [0.5, 0.5, 0]]
    return Structure(lattice=lattice,species=species,coords=coords)

@pytest.fixture
def mock_dataframe():
    """Mock table from structurelookup class"""
    # Create a simple SiO2 structure
    df = pd.DataFrame({
            'select': [False],
            'formula': ['Si O2'],
            'form_energy_per_atom': [-5.0],
            'sg': ['Cmcm'],
            'natoms': [3],
            'abc': [[5.0, 5.0, 5.0]],
            'angles': [[90.0, 90.0, 90.0]],
            'id': ['test-id']
        })
    return df


@pytest.fixture
def mock_kspacing():
    """Return a fixed kdist and bounds to avoid running real models."""
    return (0.2, 0.25, 0.15)

def test_info_input_page_file_upload(sample_cif, mock_kspacing):
    """
    Test the info input page with upload file option
    Args:
        sample_cif: BytesIO
    """
    at = AppTest.from_file("src/qe_input/pages/Intro.py")
    with patch('kspacing_model.predict_kspacing', return_value=mock_kspacing):
        at.run(timeout=10)
    assert not at.exception
    for x in at.get('selectbox'):
        if(x.label=='XC-functional'):
            # only PBEsol is available now
            assert x.options == ['PBEsol']
            x._value='PBEsol'
            x.run(timeout=10)
            assert at.session_state['functional']=='PBEsol'
        if(x.label=='pseudopotential flavour'):
            assert 'efficiency' in x.options
            assert 'precision' in x.options
            x._value='precision'
            x.run(timeout=10)
            assert at.session_state['mode']=='precision'
        if(x.label=='ML model to predict kspacing'):
            assert set(x.options) == {'RF','ALIGNN'}
            x._value='RF'
            x.run(timeout=10)
            assert at.session_state['kspacing_model']=='RF'
        if(x.label=='Confidence level'):
            x._value='0.9'
            x.run(timeout=10)
            assert at.session_state['confidence_level']==0.9
    assert at.session_state['kspacing_model']=='RF'
    assert 'structure' not in at.session_state
    for x in at.get('tab'):
        assert x.label in ['Upload structure','Search for structure']
        if(x.label == 'Upload structure'):
            with patch('kspacing_model.predict_kspacing', return_value=mock_kspacing):
                with patch('streamlit.file_uploader',return_value=sample_cif):
                    at.run(timeout=10)
                    assert at.session_state['structure']
                    assert at.session_state['structure'].formula == 'Co2 F4'
                    assert at.session_state['save_directory']
                    assert at.session_state['structure_file']
                    assert at.session_state['pseudo_family'] == 'SSSP_1.3.0_PBEsol_precision'
                    assert 'Co' in at.session_state['list_of_element_files'].keys()
                    assert 'F' in at.session_state['list_of_element_files'].keys()
                    assert at.session_state['pseudo_path']
                    assert at.session_state['cutoffs'] == {"max_ecutwfc": 90.0, "max_ecutrho": 1080.0}
                    assert at.session_state['kdist']
                    assert at.session_state['kdist_lower']
                    assert at.session_state['kdist_upper']
                    assert at.session_state['all_info']

def test_info_input_page_databases_jarvis(formula, mock_dataframe,sample_structure, mock_kspacing):
    """
    Test the info input page with looking the structure in a jarvis database
    Args:
        formula: str
        mock_dataframe: pd.DataFrame
        sample_structure: pymatgen.core.structure.Structure
    """
    # select_structure_from_table now returns a tuple (primitive_structure, structure)
    structure_tuple = (sample_structure, sample_structure)
    with patch('data_utils.StructureLookup.get_jarvis_table', return_value=mock_dataframe), \
         patch('data_utils.StructureLookup.select_structure_from_table', return_value=structure_tuple), \
         patch('kspacing_model.predict_kspacing', return_value=mock_kspacing):

        at = AppTest.from_file("src/qe_input/pages/Intro.py")
        at.run(timeout=10)
        assert not at.exception

        # Select functional
        for x in at.get('selectbox'):
            if x.label == 'XC-functional':
                assert x.options == ['PBEsol']
                x._value = 'PBEsol'
                x.run(timeout=10)
                assert at.session_state['functional'] == 'PBEsol'
            if x.label == 'pseudopotential flavour':
                x._value = 'precision'
                x.run(timeout=10)
                assert at.session_state['mode'] == 'precision'
            if x.label == 'ML model to predict kspacing':
                x._value = 'RF'
                x.run(timeout=10)
        assert at.session_state['kspacing_model'] == 'RF'
        assert 'structure' not in at.session_state
        # Enter formula and select Jarvis
        for tab in at.get('tab'):
            if tab.label == 'Search for structure':
                for input_box in at.get('text_input'):
                    input_box._value = formula
                    input_box.run(timeout=10)
                radio = at.get('radio')[0]
                radio._value = 'Jarvis'
                radio.run(timeout=10)
                at.run(timeout=10)
                assert 'structure' in at.session_state
                assert at.session_state['structure'].formula == 'Si1 O2'
                assert at.session_state['save_directory']
                assert at.session_state['structure_file']
                assert at.session_state['pseudo_family'] == 'SSSP_1.3.0_PBEsol_precision'
                assert 'Si' in at.session_state['list_of_element_files'].keys()
                assert 'O' in at.session_state['list_of_element_files'].keys()
                assert at.session_state['pseudo_path']
                assert at.session_state['cutoffs'] == {"max_ecutwfc": 75.0, "max_ecutrho": 600.0}
                assert at.session_state['kdist']
                assert at.session_state['kdist_lower']
                assert at.session_state['kdist_upper']
                assert at.session_state['all_info']


def test_info_input_page_databases_MC3D(formula, mock_dataframe,sample_structure, mock_kspacing):
    """
    Test the info input page with looking the structure in a jarvis database
    Args:
        formula: str
        mock_dataframe: pd.DataFrame
        sample_structure: pymatgen.core.structure.Structure
    """
    # select_structure_from_table now returns a tuple (primitive_structure, structure)
    structure_tuple = (sample_structure, sample_structure)
    with patch('data_utils.StructureLookup.get_mc3d_structure_table', return_value=mock_dataframe), \
         patch('data_utils.StructureLookup.select_structure_from_table', return_value=structure_tuple), \
         patch('kspacing_model.predict_kspacing', return_value=mock_kspacing):

        at = AppTest.from_file("src/qe_input/pages/Intro.py")
        at.run(timeout=10)
        assert not at.exception

        # Select functional
        for x in at.get('selectbox'):
            if x.label == 'XC-functional':
                assert x.options == ['PBEsol']
                x._value = 'PBEsol'
                x.run(timeout=10)
                assert at.session_state['functional'] == 'PBEsol'
            if x.label == 'pseudopotential flavour':
                x._value = 'precision'
                x.run(timeout=10)
                assert at.session_state['mode'] == 'precision'
            if x.label == 'ML model to predict kspacing':
                x._value = 'RF'
                x.run(timeout=10)
        assert at.session_state['kspacing_model'] == 'RF'
        assert 'structure' not in at.session_state
        # Enter formula and select Jarvis
        for tab in at.get('tab'):
            if tab.label == 'Search for structure':
                for input_box in at.get('text_input'):
                    input_box._value = formula
                    input_box.run(timeout=10)
                radio = at.get('radio')[0]
                radio._value = 'MC3D'
                radio.run(timeout=10)
                at.run(timeout=10)
                assert 'structure' in at.session_state
                assert at.session_state['structure'].formula == 'Si1 O2'
                assert at.session_state['save_directory']
                assert at.session_state['structure_file']
                assert at.session_state['pseudo_family'] == 'SSSP_1.3.0_PBEsol_precision'
                assert 'Si' in at.session_state['list_of_element_files'].keys()
                assert 'O' in at.session_state['list_of_element_files'].keys()
                assert at.session_state['pseudo_path']
                assert at.session_state['cutoffs'] == {"max_ecutwfc": 75.0, "max_ecutrho": 600.0}
                assert at.session_state['kdist']
                assert at.session_state['kdist_lower']
                assert at.session_state['kdist_upper']
                assert at.session_state['all_info']       
           
def test_info_input_page_mp_database(formula, mock_dataframe, sample_structure, mock_kspacing):
    """
    Test the info input page when selecting a structure from the MP database.
    """

    # select_structure_from_table now returns a tuple (primitive_structure, structure)
    structure_tuple = (sample_structure, sample_structure)
    with patch('data_utils.StructureLookup.get_mp_structure_table', return_value=mock_dataframe), \
         patch('data_utils.StructureLookup.select_structure_from_table', return_value=structure_tuple), \
         patch('kspacing_model.predict_kspacing', return_value=mock_kspacing):
        at = AppTest.from_file("src/qe_input/pages/Intro.py")
        at.run(timeout=10)
        assert not at.exception

        # Set XC-functional and pseudopotential flavour
        for x in at.get('selectbox'):
            if x.label == 'XC-functional':
                assert x.options == ['PBEsol']
                x._value = 'PBEsol'
                x.run(timeout=10)
                assert at.session_state['functional'] == 'PBEsol'
            if x.label == 'pseudopotential flavour':
                x._value = 'precision'
                x.run(timeout=10)
                assert at.session_state['mode'] == 'precision'
            if x.label == 'ML model to predict kspacing':
                x._value = 'RF'
                x.run(timeout=10)
        assert at.session_state['kspacing_model'] == 'RF'

        # Enter formula in "Search for structure" tab
        for tab in at.get('tab'):
            if tab.label == 'Search for structure':
                for text_input in at.get('text_input'):
                    if text_input.label == "Chemical formula (try to find structure in free databases)":
                        text_input._value = formula
                        text_input.run(timeout=10)
                # Select MP database
                for radio in at.get('radio'):
                    if 'MP' in radio.options:
                        radio._value = 'MP'
                        radio.run(timeout=10)

                # Set MP API key (mocked) in sidebar or wherever it's rendered
                for api_input in at.get('text_input'):
                    if api_input.label.startswith("Materials Project API Key"):
                        api_input._value = "dummy_mp_key"
                        api_input.run(timeout=10)

                at.run(timeout=10)
                # Assert structure was set correctly
                assert 'structure' in at.session_state
                assert at.session_state['structure'].formula == 'Si1 O2'
                assert at.session_state['save_directory']
                assert at.session_state['structure_file']
                assert at.session_state['pseudo_family'] == 'SSSP_1.3.0_PBEsol_precision'
                assert 'Si' in at.session_state['list_of_element_files'].keys()
                assert 'O' in at.session_state['list_of_element_files'].keys()
                assert at.session_state['pseudo_path']
                assert at.session_state['cutoffs'] == {"max_ecutwfc": 75.0, "max_ecutrho": 600.0}
                assert at.session_state['kdist']
                assert at.session_state['kdist_lower']
                assert at.session_state['kdist_upper']
                assert at.session_state['all_info']  


def test_info_input_page_databases_OQMD(formula, mock_dataframe,sample_structure, mock_kspacing):
    """
    Test the info input page with looking the structure in a jarvis database
    Args:
        formula: str
        mock_dataframe: pd.DataFrame
        sample_structure: pymatgen.core.structure.Structure
    """
    # select_structure_from_table now returns a tuple (primitive_structure, structure)
    structure_tuple = (sample_structure, sample_structure)
    with patch('data_utils.StructureLookup.get_oqmd_structure_table', return_value=mock_dataframe), \
         patch('data_utils.StructureLookup.select_structure_from_table', return_value=structure_tuple), \
         patch('kspacing_model.predict_kspacing', return_value=mock_kspacing):

        at = AppTest.from_file("src/qe_input/pages/Intro.py")
        at.run(timeout=10)
        assert not at.exception

        # Select functional
        for x in at.get('selectbox'):
            if x.label == 'XC-functional':
                assert x.options == ['PBEsol']
                x._value = 'PBEsol'
                x.run(timeout=10)
                assert at.session_state['functional'] == 'PBEsol'
            if x.label == 'pseudopotential flavour':
                x._value = 'precision'
                x.run(timeout=10)
                assert at.session_state['mode'] == 'precision'
            if x.label == 'ML model to predict kspacing':
                x._value = 'RF'
                x.run(timeout=10)
        assert at.session_state['kspacing_model'] == 'RF'
        assert 'structure' not in at.session_state
        # Enter formula and select Jarvis
        for tab in at.get('tab'):
            if tab.label == 'Search for structure':
                for input_box in at.get('text_input'):
                    input_box._value = formula
                    input_box.run(timeout=10)
                radio = at.get('radio')[0]
                radio._value = 'OQMD'
                radio.run(timeout=10)
                at.run(timeout=10)
                assert 'structure' in at.session_state
                assert at.session_state['structure'].formula == 'Si1 O2'
                assert at.session_state['save_directory']
                assert at.session_state['structure_file']
                assert at.session_state['pseudo_family'] == 'SSSP_1.3.0_PBEsol_precision'
                assert 'Si' in at.session_state['list_of_element_files'].keys()
                assert 'O' in at.session_state['list_of_element_files'].keys()
                assert at.session_state['pseudo_path']
                assert at.session_state['cutoffs'] == {"max_ecutwfc": 75.0, "max_ecutrho": 600.0}
                assert at.session_state['kdist']
                assert at.session_state['kdist_lower']
                assert at.session_state['kdist_upper']
                assert at.session_state['all_info']            

def test_pseudos(ELEMENTS):
    """
    Test that the pseudos and pseudo_cutoffs folders exist and that they contain the correct files
    """
    assert os.path.exists('./src/qe_input/pseudos/')
    assert os.path.exists('./src/qe_input/pseudo_cutoffs/')
    pseudos_root = './src/qe_input/pseudos/'
    list_of_pseudo_types = [
        name
        for name in os.listdir(pseudos_root)
        if os.path.isdir(os.path.join(pseudos_root, name))
    ]
    if ".DS_Store" in list_of_pseudo_types:
        list_of_pseudo_types.remove(".DS_Store")
    list_of_cutoffs=os.listdir('./src/qe_input/pseudo_cutoffs/')
    if ".DS_Store" in list_of_cutoffs:
        list_of_cutoffs.remove(".DS_Store")

    # check that for each combination of functional and mode there is a folder
    # that each folder contains psudos for all elements
    at = AppTest.from_file("src/qe_input/pages/Intro.py")
    at.run(timeout=10)
    for x in at.get('selectbox'):
        if(x.label=='XC-functional'):
            functional_options=x.options
        if(x.label=='pseudopotential flavour'):
            mode_options=x.options
    assert functional_options == ['PBEsol']
    assert 'efficiency' in mode_options
    assert 'precision' in mode_options
    assert len(mode_options) == 2

    for functional in functional_options:
        for mode in mode_options:
            switch_pseudo=0
            switch_cutoff=0
            for pseudo in list_of_pseudo_types:
                if(functional in pseudo and mode in pseudo):
                    switch_pseudo=1
            for cutoff_name in list_of_cutoffs:
                if(functional in cutoff_name and mode in cutoff_name):
                    switch_cutoff=1
            assert switch_pseudo, f"Missing cutoff file for {functional}-{mode} combination"
            assert switch_cutoff, f"Missing cutoff file for {functional}-{mode} combination"

    for folder in list_of_pseudo_types:
        list_of_files = os.listdir(os.path.join(pseudos_root, folder))
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