import os
import sys
from pymatgen.core.structure import Structure
from dotenv import load_dotenv
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/qe_input')))
load_dotenv()


from data_utils import jarvis_structure_lookup, mp_structure_lookup, mc3d_structure_lookup,oqmd_strucutre_lookup

@pytest.fixture
def formula():
    return 'SiO2'

def test_jarvis_lookup(formula):
    structure=jarvis_structure_lookup(formula)
    assert isinstance(structure,Structure)

def test_mp_lookup(formula):
    mp_api_key=os.environ.get('MP_API_KEY')
    structure=mp_structure_lookup(formula, mp_api_key)
    assert isinstance(structure,Structure)

def test_mc3d_lookup(formula):
    structure=mc3d_structure_lookup(formula)
    assert isinstance(structure,Structure)

def test_oqmd_lookup(formula):
    structure=oqmd_strucutre_lookup(formula)
    assert isinstance(structure,Structure)