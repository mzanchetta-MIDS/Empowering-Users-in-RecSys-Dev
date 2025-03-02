# pages/saved_for_later.py
import streamlit as st

def show_saved_for_later():
    st.subheader("Your library")
    
    # Make sure saved_for_later exists
    if "saved_for_later" not in st.session_state.user_profile:
        st.session_state.user_profile["saved_for_later"] = []
    
    saved_books = st.session_state.user_profile["saved_for_later"]

    if not saved_books:
        st.info("You haven't saved any books yet!")
        return
    
    # Display saved books in columns (up to 3 per row)
    max_cols = min(len(saved_books), 3)
    cols = st.columns(max_cols)
    
    for idx, book in enumerate(saved_books):
        col_num = idx % max_cols
        with cols[col_num]:
            with st.container():
                # Card styling with HTML
                st.markdown(f"""
                <div style="background-color:#2C2C2C; 
                            padding:15px; 
                            border-radius:10px;
                            margin-bottom:20px;">
                    <h4>📖 {book['title']}</h4>
                    <p><strong>Author:</strong> {book['author']}</p>
                    <p><strong>Description:</strong> {book['description']}</p>
                    <p><strong>Why this was recommended:</strong> {book['explanation']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Read it? Provide a rating
                st.write("✓ Read it? Provide a rating:")
                
                # Show 5-star rating system
                rating_cols = st.columns(5)
                for i in range(5):
                    star_num = i + 1
                    with rating_cols[i]:
                        if st.button("★", key=f"lib_rate_{star_num}_{book['title']}"):
                            # Initialize ratings dictionary if needed
                            if "ratings" not in st.session_state.user_profile:
                                st.session_state.user_profile["ratings"] = {}
                            
                            # Save the rating
                            st.session_state.user_profile["ratings"][book["title"]] = star_num
                            
                            # Remove from library
                            st.session_state.user_profile["library"] = [
                                b for b in library_books if b["title"] != book["title"]
                            ]
                            st.rerun()
                
                if st.button("✗ No Longer Interested", key=f"not_int_saved_{book['title']}"):
                    if "not_interested" not in st.session_state.user_profile:
                        st.session_state.user_profile["not_interested"] = []
                    
                    # Add to not_interested
                    st.session_state.user_profile["not_interested"].append(book["title"])
                    
                    # Remove from saved_for_later
                    st.session_state.user_profile["saved_for_later"] = [
                        b for b in saved_books if b["title"] != book["title"]
                    ]
                    st.rerun()