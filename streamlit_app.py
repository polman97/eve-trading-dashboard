import streamlit as st
import pandas as pd
from app.db.db import get_insights_full
import sys
import os
print("SYS PATH:", sys.path)
print("CWD:", os.getcwd())


df = get_insights_full()
st.dataframe(df)

