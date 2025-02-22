# pages/recommendations.py
import streamlit as st
from utils.data_utils import get_sample_recommendations

def show_recommendations():
    st.subheader("📚 Your Personalized Book Recommendations")

    # Fetch recommendations dynamically if not already in session
    if "recommendations_list" not in st.session_state:
        st.session_state.recommendations_list = get_sample_recommendations()

    recs = st.session_state.recommendations_list

    # Initialize the user_profile field for 'saved_for_later'
    if "saved_for_later" not in st.session_state.user_profile:
        st.session_state.user_profile["saved_for_later"] = []

    num_recs = len(recs)

    # ✅ 1) Handle zero-recommendation case to avoid columns(0)
    if num_recs == 0:
        st.info("No more recommendations at this time! Check Saved for Later or come back soon.")
        return

    # Limit to a maximum of 3 columns per row
    max_cols = min(num_recs, 3)
    cols = st.columns(max_cols)  # e.g., 3 columns if 3 or more recs

    for idx, rec in enumerate(recs):
        # Place each recommendation in one of the columns
        col_num = idx % max_cols
        with cols[col_num]:
            with st.container():
                # Card styling with HTML
                st.markdown(f"""
                <div style="background-color:#2C2C2C; 
                            padding:15px; 
                            border-radius:10px;
                            margin-bottom:20px;">
                    <h4 style="margin-top:5px;">📖 {rec['title']}</h4>
                    <p><strong>Author:</strong> {rec['author']}</p>
                    <p><strong>Description:</strong> {rec['description']}</p>
                    <p><strong>Why this was recommended:</strong> {rec['explanation']}</p>
                </div>
                """, unsafe_allow_html=True)

                # ✅ 2) Stack each button vertically

                if st.button("📚 Save for Later", key=f"save_{idx}"):
                    # Move book to 'saved_for_later'
                    st.session_state.user_profile["saved_for_later"].append(rec)  # store the entire rec dict
                    # Remove from current recs
                    st.session_state.recommendations_list.pop(idx)
                    st.rerun()

                if st.button("✓ Already Read It", key=f"read_{idx}"):
                    # Mark in user profile as 'already_read'
                    already_read = st.session_state.user_profile.get("already_read", [])
                    already_read.append(rec["title"])
                    st.session_state.user_profile["already_read"] = already_read
                    st.session_state.recommendations_list.pop(idx)
                    st.rerun()

                if st.button("✗ Not Interested", key=f"not_int_{idx}"):
                    # Mark in user profile as 'not_interested'
                    not_interested = st.session_state.user_profile.get("not_interested", [])
                    not_interested.append(rec["title"])
                    st.session_state.user_profile["not_interested"] = not_interested
                    st.session_state.recommendations_list.pop(idx)
                    st.rerun()

                if st.button("ℹ️ I'd Like to Know More", key=f"info_{idx}"):
                    # Just set some placeholder or navigate to profile
                    st.session_state["tabs"] = "Profile"
                    st.rerun()
