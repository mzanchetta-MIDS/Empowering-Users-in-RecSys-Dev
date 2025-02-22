import streamlit as st

def show_reading_goals():
    st.title("Reading Goals")

    goals = [
        "Older classics",
        "The latest best-sellers",
        "Award-winning books",
        "New genres I haven't explored",
        "Books similar to my favorites",
        "Less-reviewed gems",
        "Highly-rated selections",
        "Quick reads",
        "Long, immersive reads"
    ]

    if "reading_goals" not in st.session_state:
        st.session_state.reading_goals = []
    if "other_goals" not in st.session_state:
        st.session_state.other_goals = ""

    selected_goals = st.multiselect(
        "Are you trying to read more of any particular type of book?",
        options=goals,
        default=st.session_state.reading_goals
    )
    st.session_state.reading_goals = selected_goals

    # Optional text area for additional goals
    other_goals = st.text_area(
        "Any other reading goals? (optional)",
        value=st.session_state.other_goals
    )
    st.session_state.other_goals = other_goals

    # Navigation
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("← Back"):
            st.session_state.page = "favorite_books"
            st.rerun()
    with col2:
        if st.button("Next →") and (st.session_state.reading_goals or
                                    st.session_state.other_goals.strip()):
            st.session_state.page = "completion"
            st.rerun()
