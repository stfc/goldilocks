import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/qe_input')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/qe_input/pages')))

from streamlit.testing.v1 import AppTest


def test_the_generation_button():
    at = AppTest.from_file("src/qe_input/pages/Deterministic_generator.py")
    at.run()
    assert at.get('button')==[]
    at = AppTest.from_file("src/qe_input/pages/Deterministic_generator.py")
    at.session_state['all_info']=True
    at.run()
    assert at.get('button')!=[]