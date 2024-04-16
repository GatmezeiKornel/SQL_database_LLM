import hmac
import os
import streamlit as st

def password_entered():
    """Checks whether a password entered by the user is correct."""
    if hmac.compare_digest(st.session_state["password"], os.environ["streamlit_password"]):
        st.session_state["password_correct"] = True
        # del st.session_state["password"]  # Don't store the password.
    else:
        st.session_state["password_correct"] = False

def check_password():
    """Returns `True` if the user had the correct password."""

    # Return True if the password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password.
    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )

    if "password_correct" in st.session_state:
        st.error("Password incorrect")
    return False

def set_config():
    """Sets the page wide mode"""
    st.set_page_config(layout="wide")