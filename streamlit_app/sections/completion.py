import streamlit as st
import time
from utils.profile_utils import save_profile

def show_completion():
    st.success("""
    Thanks for telling us about your reading preferences! We're using your responses 
    to craft personalized book recommendations tailored just for you.
    """)

    with st.spinner('Preparing your personalized recommendations...'):
        save_profile()
        time.sleep(1)

    # Animated book icon
    st.markdown("""
        <div style="display: flex; justify-content: center; margin: 30px 0;">
            <div class="book">
                <div class="book__page"></div>
                <div class="book__page"></div>
                <div class="book__page"></div>
            </div>
        </div>
        <style>
            .book {
                width: 100px;
                height: 120px;
                position: relative;
                perspective: 800px;
            }
            .book__page {
                position: absolute;
                width: 100%;
                height: 100%;
                top: 0;
                left: 0;
                background-color: #4e7694;
                transform-origin: left center;
                transition: transform 0.8s ease-in-out;
                border-radius: 5px;
                box-shadow: 0 0 5px rgba(0, 0, 0, 0.1);
            }
            .book__page:nth-child(1) {
                animation: flipPage1 3s infinite;
            }
            .book__page:nth-child(2) {
                animation: flipPage2 3s infinite;
            }
            .book__page:nth-child(3) {
                animation: flipPage3 3s infinite;
            }
            @keyframes flipPage1 {
                0%, 20% { transform: rotateY(0deg); }
                30%, 70% { transform: rotateY(-130deg); }
                80%, 100% { transform: rotateY(0deg); }
            }
            @keyframes flipPage2 {
                0%, 30% { transform: rotateY(0deg); }
                40%, 80% { transform: rotateY(-130deg); }
                90%, 100% { transform: rotateY(0deg); }
            }
            @keyframes flipPage3 {
                0%, 40% { transform: rotateY(0deg); }
                50%, 90% { transform: rotateY(-130deg); }
                100% { transform: rotateY(0deg); }
            }
        </style>
        """, unsafe_allow_html=True)
    
    st.markdown("""
        <div style="text-align: center; margin-top: 20px;">
            <h3 style="color: #4e7694;">Your BookWise profile is ready!</h3>
            <p>We're excited to show you personalized recommendations based on your preferences.</p>
        </div>
        """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Enter BookWise!", type="primary", use_container_width=True):
            st.session_state.profile_completed = True
            st.session_state.selected_tab = "Recommendations"
            st.rerun()
