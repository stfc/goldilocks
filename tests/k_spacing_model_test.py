import sys
import os
from pymatgen.core.structure import Structure
from kspacing_model import predict_kspacing
from data_utils import jarvis_structure_lookup
import pytest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/qe_input')))


@pytest.fixture
def structure():
    structure=jarvis_structure_lookup('SiO2')
    return structure

def test_predict_kspacing(structure):
    kspacing=predict_kspacing(structure)
    assert isinstance(kspacing,float)