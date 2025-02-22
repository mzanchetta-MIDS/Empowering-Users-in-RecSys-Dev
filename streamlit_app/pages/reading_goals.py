import streamlit as st
from utils.data_utils import get_reading_goals
from utils.profile_utils import save_reading_goals

def show_reading_goals():
    st.title("Reading Goals")

    # Load default reading goals
    default_goals = get_reading_goals()
    current_goals = st.session_state.user_profile.get("reading_goals", [])

    # --- FORM: So the dropdown stays open for multiple selections ---
    with st.form("reading_goals_form", clear_on_submit=False):
        st.write("Select your reading goals, then click 'Submit' to apply.")

        # Multi-select for predefined reading goals
        selected_goals = st.multiselect(
            "Are you trying to read more of any particular type of book?",
            options=default_goals,
            default=current_goals
        )

        submitted = st.form_submit_button("Submit Reading Goals")

    # If user clicked "Submit Reading Goals", update session state
    if submitted:
        save_reading_goals(selected_goals, "")
        st.rerun()

    # --- NAVIGATION BUTTONS ---
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("← Back"):
            st.session_state.page = "favorite_books"
            st.rerun()

    with col2:
        # Let them proceed if they want. If you require at least 1 goal, do:
        #   if st.button("Next →") and selected_goals:
        if st.button("Next →"):
            st.session_state.page = "completion"
            st.rerun()
