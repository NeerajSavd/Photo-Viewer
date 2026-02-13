import streamlit as st
from search import search, on_this_day, get_image_details
from image_tagging import run_analysis
from datetime import datetime
import os
from PIL import Image, ImageOps
from collections import defaultdict
import time

st.set_page_config(
    page_title="Photos",
    page_icon="📸",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main {
        background-color: #0f0f0f;
        padding-top: 0;
    }
    .block-container {
        padding-top: 20px;
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
        border-radius: 20px;
        padding: 0px 10px 0px 10px;
    }
    .stButton>button:hover {
        background-color: #2a3a6b;
    }
    .stTextInput>div>div {
        border-radius: 25px;
        overflow: hidden;
    }
    .stImage {
        max-width: 300px;
    }
    .stDataFrame {
        background-color: #1e1e1e;
    }
    /* Optimize loading spinner */
    .stSpinner > div {
        border: 3px solid #1e2a56;
        border-top-color: #2a3a6b;
        animation: spin 1s linear infinite;
    }
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    /* Reduce image loading delay */
    .stImage img {
        image-rendering: auto;
    }
</style>
""", unsafe_allow_html=True)

if 'query' not in st.session_state:
    st.session_state.query = ''
if 'images' not in st.session_state:
    st.session_state.images = None
if 'page_number' not in st.session_state:
    st.session_state.page_number = 0
if 'city' not in st.session_state:
    st.session_state.city = ''
if 'dateStart' not in st.session_state:
    st.session_state.dateStart = None
if 'dateEnd' not in st.session_state:
    st.session_state.dateEnd = None
if 'loading_search' not in st.session_state:
    st.session_state.loading_search = False

IMAGES_PER_PAGE = 20
COLUMNS_PER_PAGE = 3
MAX_IMAGE_SIZE = (800, 800)  # Resize images for display

@st.cache_data(ttl=3600)
def get_image_details_cached(img_path):
    """Cache image details to avoid repeated processing"""
    return get_image_details(img_path)

@st.cache_data(ttl=3600)
def get_image_thumbnail(img_path):
    """Cache image thumbnails for faster loading"""
    try:
        if os.path.exists(img_path):
            image = Image.open(img_path)
            image = ImageOps.exif_transpose(image)
            # Resize for thumbnail
            image.thumbnail(MAX_IMAGE_SIZE, Image.Resampling.LANCZOS)
            return image
    except Exception as e:
        st.error(f"Error loading image: {e}")
    return None

def create_image_card(img_path):
    def open_explorer():
        folder = os.path.dirname(os.path.abspath(img_path))
        if os.path.exists(folder):
            os.startfile(folder)
    def open_image():
        os.startfile(img_path)
    
    # Show thumbnail first for faster loading
    with st.spinner("Loading image..."):
        thumbnail = get_image_thumbnail(img_path)
    
    if thumbnail:
        st.image(thumbnail)
    
    # Create details button
    if st.button("Details", key=f"details_{img_path}"):
        with st.spinner("Getting details..."):
            st.session_state.current_image = img_path
            st.session_state.current_details = get_image_details_cached(img_path)

@st.cache_data(ttl=3600)
def get_on_this_day_images():
    """Cache on this day images to avoid repeated calls"""
    return on_this_day()

def create_on_this_day_view():
    st.title("On This Day")
    st.subheader(datetime.now().strftime('%B %d, %Y'))

    images = get_on_this_day_images()
    if not images:
        st.info("No images found for today.")
        return
    
    images_by_date = defaultdict(list)
    for year in images:
        images_by_date[year[0]] = year[1]
    
    # Two-column layout: images on left, details on right
    col1, col2 = st.columns([3, 1])
    
    with col1:
        with st.container(height=1200):
            for date_str, date_images in images_by_date.items():
                st.markdown(f"### {date_str}")
                     
                cols = st.columns(COLUMNS_PER_PAGE)
                for idx, img_path in enumerate(date_images):
                    with cols[idx % COLUMNS_PER_PAGE]:
                        create_image_card(img_path)
    
    with col2:
        # Show details panel on the right side with its own scroll
        st.markdown("### Image Details")
        with st.container(height=600):
            if st.session_state.get('current_image'):
                details = st.session_state.current_details
                 
                st.markdown(f"**File Path:**")
                st.code(st.session_state.current_image, language=None)
                 
                st.markdown(f"**Timestamp:** {details.get('timestamp', 'N/A')}")
                st.markdown(f"**Camera Model:** {details.get('camera_model', 'N/A')}")
                st.markdown(f"**Latitude:** {details.get('latitude', 'N/A')}")
                st.markdown(f"**Longitude:** {details.get('longitude', 'N/A')}")
                 
                st.markdown(f"**Tags:**")
                if details.get('tags'):
                    for tag in details['tags']:
                        st.markdown(f"- {tag}")
                else:
                    st.markdown("*No tags found*")
            else:
                st.info("Click 'Details' on an image to see its details here.")

def create_search_view():
    st.title("Search Results")
    
    # Navigation buttons - use state change instead of rerun
    col1, col2, col3 = st.columns([1, 1, 1])
    if st.session_state.page_number > 0:
        with col1:
            if st.button("← Previous", key="prev"):
                st.session_state.page_number -= 1
    with col2:
        st.write(f"Page {st.session_state.page_number + 1} of {(len(st.session_state.images) + IMAGES_PER_PAGE - 1) // IMAGES_PER_PAGE}")
    if st.session_state.page_number < len(st.session_state.images) // IMAGES_PER_PAGE - 1:
        with col3:
            if st.button("Next →", key="next"):
                st.session_state.page_number += 1
    
    if not st.session_state.images or len(st.session_state.images) == 0:
        st.info("Enter a search query to find images.")
        return

    st.divider()
    start_idx = st.session_state.page_number * IMAGES_PER_PAGE
    end_idx = start_idx + IMAGES_PER_PAGE
    current_images = st.session_state.images[start_idx:end_idx]
    
    if not current_images:
        st.info("No more images on this page.")
        return
    
    # Show loading indicator if needed
    if st.session_state.get('loading_search'):
        with st.spinner("Loading images..."):
            time.sleep(0.1)  # Small delay to show spinner
            st.session_state.loading_search = False
    
    # Two-column layout: images on left, details on right
    col1, col2 = st.columns([3, 1])
    with col1:
        with st.container(height=1200):
            cols = st.columns(COLUMNS_PER_PAGE)
            for idx, img_path in enumerate(current_images):
                with cols[idx % COLUMNS_PER_PAGE]:
                    create_image_card(img_path)
    
    with col2:
        # Show details panel on the right side with its own scroll
        st.markdown("### Image Details")
        with st.container(height=600):
            if st.session_state.get('current_image'):
                details = st.session_state.current_details
                
                st.markdown(f"**File Path:**")
                st.code(st.session_state.current_image, language=None)
                
                st.markdown(f"**Timestamp:** {details.get('timestamp', 'N/A')}")
                st.markdown(f"**Camera Model:** {details.get('camera_model', 'N/A')}")
                st.markdown(f"**Latitude:** {details.get('latitude', 'N/A')}")
                st.markdown(f"**Longitude:** {details.get('longitude', 'N/A')}")
                
                st.markdown(f"**Tags:**")
                if details.get('tags'):
                    for tag in details['tags']:
                        st.markdown(f"- {tag}")
                else:
                    st.markdown("*No tags found*")
            else:
                st.info("Click 'Details' on an image to see its details here.")

@st.cache_data(ttl=3600)
def perform_search(search_query, city, date_start, date_end):
    """Cache search results to avoid repeated searches"""
    return search(search_query, city, date_start, date_end)

def create_sidebar():
    with st.sidebar:
        st.markdown("### Search")
        
        search_query = st.text_input(
            "Search Query",
            value=st.session_state.query,
            key="search_input",
            placeholder="Search your library..."
        )
        city_input = st.text_input(
            "City",
            value=st.session_state.city,
            key="city_input",
            placeholder="Enter city name..."
        )
        st.divider()
        
        st.markdown("### Date Range")
        start_date = st.date_input(
            "Start Date",
            value=st.session_state.dateStart,
            min_value=datetime(2000, 1, 1),
            max_value=datetime.now(),
            key="start_date"
        )
        end_date = st.date_input(
            "End Date",
            value=st.session_state.dateEnd,
            min_value=datetime(2000, 1, 1),
            max_value=datetime.now(),
            key="end_date"
        )
        
        if st.button("Search", key="search_btn"):
            st.session_state.loading_search = True
            st.session_state.query = search_query
            st.session_state.city = city_input
            st.session_state.dateStart = start_date
            st.session_state.dateEnd = end_date
            st.session_state.images = perform_search(search_query, city_input, start_date, end_date)
            st.session_state.page_number = 0
            st.rerun()

def main():
    create_sidebar()
    
    if st.session_state.query:
        create_search_view()
    else:
        create_on_this_day_view()
if __name__ == "__main__":
    main()
