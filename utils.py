import os
import numpy as np
import pandas as pd
import string
import streamlit as st
from typing import List
import os

FIXED = 2
FLOATING = 1
FORBIDDEN = 0

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data")
# LOGO_PATH = os.path.join(os.path.dirname(__file__), "..", "logo_v2.png")
LOGO_PATH = os.path.join(os.path.dirname(__file__), "enjoy_option.png")

def get_logo():
    """Load the WORDLEr logo."""
    a, b, c = st.columns([1, 5, 1])
    with b:
        st.image(LOGO_PATH, use_column_width='auto')
        st.markdown(' ')