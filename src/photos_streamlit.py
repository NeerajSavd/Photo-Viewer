import streamlit as st
from search import search, on_this_day
from image_tagging import run_analysis
from datetime import datetime
import os
from collections import defaultdict

st.set_page_config(
    page_title="Photo Library",
    page_icon="📸",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main {
        background-color: #0f0f0f;
    }
    h1 {
        color: #ffffff;
        font-size: 3rem;
        text-align: center;
    }
    h2 {
        color: #ffffff;
        font-size: 2rem;
    }
    .stButton>button {
        background-color: #1e2a56;
        color: white;
        border-radius: 25px;
        padding: 10px 20px;
    }
    .stButton>button:hover {
        background-color: #2a3a6b;
    }
    .stTextInput>div>div>input {
        background-color: #333333;
        color: white;
        border-radius: 25px;
    }
    .stImage {
        max-width: 300px;
    }
    .stDataFrame {
        background-color: #1e1e1e;
    }
</style>
""", unsafe_allow_html=True)

if 'query' not in st.session_state:
    st.session_state.query = ''
if 'images' not in st.session_state:
    st.session_state.images = None
if 'page_number' not in st.session_state:
    st.session_state.page_number = 0

IMAGES_PER_PAGE = 20

def create_image_card(img_path):
    """Create a card with image and click handlers"""
    col1, col2 = st.columns([1, 4])
    
    with col1:
        try:
            # Display image with thumbnail
            if os.path.exists(img_path):
                st.image(img_path, use_column_width=True, caption=os.path.basename(img_path))
        except Exception as e:
            st.error(f"Error loading image: {e}")
    
    with col2:
        st.markdown(f"""
        <div style="background-color: #1e1e1e; padding: 15px; border-radius: 10px; margin: 10px;">
            <h3 style="color: #ffffff; margin: 0 0 10px 0;">{os.path.basename(img_path)}</h3>
            <p style="color: #aaaaaa; margin: 5px 0;">{img_path}</p>
            <div style="margin-top: 10px;">
                <button onclick="window.open('{img_path}', '_blank')" 
                        style="background-color: #1e2a56; color: white; border: none; padding: 8px 16px; 
                               border-radius: 5px; cursor: pointer; margin-right: 10px;">
                    Open Image
                </button>
                <button onclick="window.open('{os.path.dirname(img_path)}', '_blank')" 
                        style="background-color: #1e2a56; color: white; border: none; padding: 8px 16px; 
                               border-radius: 5px; cursor: pointer;">
                    Open Folder
                </button>
            </div>
        </div>
        """, unsafe_allow_html=True)

def create_on_this_day_view():
    st.title("On This Day")
    st.subheader(datetime.now().strftime('%B %d, %Y'))

    images = on_this_day()
    if not images:
        st.info("No images found for today.")
        return
    
    images_by_date = defaultdict(list)
    for year in images:
        images_by_date[year[0]] = year[1]
    
    for date_str, date_images in images_by_date.items():
        st.markdown(f"### {date_str}")
        
        cols = st.columns(3)
        for idx, img_path in enumerate(date_images):
            with cols[idx % 3]:
                try:
                    if os.path.exists(img_path):
                        st.image(img_path)
                except Exception as e:
                    st.error(f"Error loading image: {e}")

def create_search_view():
    st.title("Search Results")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("← Back", key="back"):
            st.session_state.query = ''
            st.session_state.images = None
            st.session_state.page_number = 0
            st.rerun()
    
    with col2:
        st.write(f"Page {st.session_state.page_number + 1}")
    
    with col3:
        if st.button("Next →", key="next"):
            st.session_state.page_number += 1
            st.rerun()
    
    st.divider()
    if not st.session_state.images:
        st.info("Enter a search query to find images.")
        return
    
    start_idx = st.session_state.page_number * IMAGES_PER_PAGE
    end_idx = start_idx + IMAGES_PER_PAGE
    current_images = st.session_state.images[start_idx:end_idx]
    
    if not current_images:
        st.info("No more images on this page.")
        return
    
    cols = st.columns(3)
    for idx, img_path in enumerate(current_images):
        with cols[idx % 3]:
            create_image_card(img_path)
    
    st.divider()
    num_pages = (len(st.session_state.images) + IMAGES_PER_PAGE - 1) // IMAGES_PER_PAGE
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.session_state.page_number > 0:
            if st.button("← Previous", key="prev"):
                st.session_state.page_number -= 1
                st.rerun()
    
    with col2:
        st.write(f"Page {st.session_state.page_number + 1} of {num_pages}")
    
    with col3:
        if st.session_state.page_number < num_pages - 1:
            if st.button("Next →", key="next_page"):
                st.session_state.page_number += 1
                st.rerun()

def main():
    if st.session_state.query:
        create_search_view()
    else:
        create_on_this_day_view()

if __name__ == "__main__":
    main()
