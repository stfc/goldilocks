import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/qe_input')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/qe_input/pages')))

from streamlit.testing.v1 import AppTest


def test_parent_page():
    at = AppTest.from_file("src/qe_input/QE_input.py")
    at.run()
    assert not at.exception
    at.switch_page("pages/README.py")
    at.run()
    assert not at.exception
    at.switch_page("pages/Intro.py")
    at.run()
    assert not at.exception
    at.switch_page("pages/Chatbot_generator.py")
    at.run()
    assert not at.exception
    at.switch_page("pages/Deterministic_generator.py")
    at.run()
    assert not at.exception