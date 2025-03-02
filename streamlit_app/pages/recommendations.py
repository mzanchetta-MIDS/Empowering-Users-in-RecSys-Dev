# pages/recommendations.py
import streamlit as st
from utils.data_utils import get_sample_recommendations
from utils.profile_utils import save_profile
from streamlit_star_rating import st_star_rating

def get_new_recommendations():
    """Get new recommendations the user hasn't seen yet"""
    all_recommendations = get_sample_recommendations()
    
    # Filter out books the user has already interacted with
    already_seen = []
    
    # Add books from already_read list to already_seen
    if "already_read" in st.session_state.user_profile:
        already_seen.extend(st.session_state.user_profile["already_read"])
    
    # Add books from not_interested list to already_seen
    if "not_interested" in st.session_state.user_profile:
        already_seen.extend(st.session_state.user_profile["not_interested"])
    
    # Add books currently in saved_for_later
    if "saved_for_later" in st.session_state.user_profile:
        for book in st.session_state.user_profile["saved_for_later"]:
            if "title" in book:
                already_seen.append(book["title"])
    
    # Get books the user hasn't seen
    new_recommendations = [r for r in all_recommendations if r["title"] not in already_seen]
    
    # Take up to 3 new recommendations
    return new_recommendations[:3]

def show_ratings(book_title, key_prefix):
    """Display 5-star rating widget and handle selection"""
    st.write("Rate this book:")
    
    cols = st.columns(5)
    rating = 0
    
    # Create 5 star buttons
    for i in range(5):
        star_num = i + 1
        with cols[i]:
            if st.button("★", key=f"{key_prefix}_star_{star_num}_{book_title}"):
                rating = star_num
                
                # Initialize ratings dictionary if it doesn't exist
                if "ratings" not in st.session_state.user_profile:
                    st.session_state.user_profile["ratings"] = {}
                
                # Save the rating
                st.session_state.user_profile["ratings"][book_title] = rating
                
                # Remove from recommendations
                st.session_state.recommendations_list = [
                    book for book in st.session_state.recommendations_list 
                    if book["title"] != book_title
                ]
                st.rerun()

def show_recommendations():
    st.subheader("Your Book Recommendations")
    st.write('''Below are three personalized book recommendations, 
    each with a customized explanation about why we think you'll like it. 
    As you respond to the recommendations with the buttons below, 
    our system will better learn your preferences and provide you with new recommendations!
    Once you've gone through these, click 'Get More Recommendations' for a new batch!''')

    # Initialize recommendations_list if it doesn't exist
    if "recommendations_list" not in st.session_state:
        st.session_state.recommendations_list = get_new_recommendations()
    
    recommendations = st.session_state.recommendations_list
    
    if not recommendations:
        st.info("You've gone through your latest batch of recommendations! Click below to get more.")
        
        # Add button to get more recommendations
        if st.button("Get More Recommendations"):
            st.session_state.recommendations_list = get_new_recommendations()
            st.rerun()
        return
    
    # Display recommendations in columns (up to 3 per row)
    max_cols = min(len(recommendations), 3)
    cols = st.columns(max_cols)
    
    for idx, rec in enumerate(recommendations):
        col_num = idx % max_cols
        with cols[col_num]:
            with st.container():
                # Card styling with HTML          
                st.markdown(f"""
                <div class="recommendation-card">
                    <div class="card-content">
                        <h4 style="margin-top:5px;"><span style="color:#EC5A53;">♦</span> {rec['title']}</h4>
                        <p><strong>Author:</strong> {rec['author']}</p>
                        <p><strong>Description:</strong> {rec['description']}</p>
                        <p><strong>Why this was recommended:</strong> {rec['explanation']}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Action buttons
                if st.button("Save to Library", key=f"save_{rec['title']}"):
                    # Set pending action to be processed in main app loop
                    st.session_state.pending_action = {
                        "type": "save",
                        "title": rec["title"]
                    }
                    st.rerun()
                                
                if st.button("✗ Not Interested", key=f"not_int_{rec['title']}"):
                    if "not_interested" not in st.session_state.user_profile:
                        st.session_state.user_profile["not_interested"] = []
                    
                    # Add to not_interested with author
                    formatted_title = f"{rec['title']} - {rec['author']}"
                    st.session_state.user_profile["not_interested"].append(formatted_title)
                    
                    # Then also call save_profile to persist changes
                    from utils.profile_utils import save_profile
                    save_profile()

                    # Remove from recommendations
                    st.session_state.recommendations_list = [
                        book for book in recommendations if book["title"] != rec["title"]
                    ]
                    st.rerun()

                # Two columns: first for the label, second for the star widget
                col_label, col_stars = st.columns([1.36, 1])  

                with col_label:
                    st.markdown("""
                        <div style="display: flex; height: 40px; align-items: center; justify-content: center; text-align: center;">
                            <p style="margin: 0; padding: 0;">Already read it? Provide a rating:</p>
                        </div>
                    """, unsafe_allow_html=True)

                with col_stars:
                    rating = st_star_rating(
                        label="",
                        maxValue=5,
                        defaultValue=0,
                        key=f"rating_{rec['title']}",
                        dark_theme=False,
                        customCSS=".react-stars {margin-top: -15px; background-color: #E6E3DC !important; color: #9C897E;}"
                    )

                    if rating > 0:
                        if "ratings" not in st.session_state.user_profile:
                            st.session_state.user_profile["ratings"] = {}
                        formatted_title = f"{rec['title']} - {rec['author']}"
                        st.session_state.user_profile["ratings"][formatted_title] = rating
                        
                        # Save to profile 
                        from utils.profile_utils import save_profile
                        save_profile()
                        
                        # Remove from recommendations
                        st.session_state.recommendations_list = [
                            book for book in recommendations if book["title"] != rec["title"]
                        ]
                        st.rerun()

