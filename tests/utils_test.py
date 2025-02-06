import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/qe_input')))

from utils import generate_input_file

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

# test to check the generate_input_file function
def test_generate_input_file(tmp_path):
    mock_file = tmp_path / 'mock_structure.cif'
    mock_file.write_text(CIF, encoding="utf-8")
    pseudo_path = tmp_path / 'pseudos'
    pseudo_Co = pseudo_path / 'Co.upf'
    pseudo_F = pseudo_path / 'F.upf'
    dict_pseudo_file_names = {'Co':'Co.upf','F':'F.upf'}
    max_ecutwfc = 30
    max_ecutrho = 240
    kspacing = 10
    
    generated_file = generate_input_file(tmp_path, mock_file, pseudo_path, dict_pseudo_file_names, max_ecutwfc, max_ecutrho, kspacing)
    filename = tmp_path / 'qe.in'

    assert generated_file
    assert os.path.isfile(filename)
