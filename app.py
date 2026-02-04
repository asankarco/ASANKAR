import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
import json

# Page configuration
st.set_page_config(
    page_title="Product Gallery",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stImage, .stVideo {
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .tag-container {
        margin-top: 1rem;
        padding: 1rem;
        background-color: #f8f9fa;
        border-radius: 8px;
    }
    .tag-label {
        font-weight: 600;
        color: #495057;
        margin-bottom: 0.3rem;
    }
    .tag-value {
        color: #6c757d;
        margin-bottom: 0.8rem;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_google_sheets_client():
    """Initialize Google Sheets API client using service account credentials"""
    try:
        # Method 1: Try to load as JSON string (RECOMMENDED - NO FORMATTING ISSUES!)
        if "gcp_service_account_json" in st.secrets:
            json_str = st.secrets["gcp_service_account_json"]
            credentials_dict = json.loads(json_str)
            
        # Method 2: Load from individual fields (OLD METHOD)
        elif "gcp_service_account" in st.secrets:
            credentials_dict = dict(st.secrets["gcp_service_account"])
            
        else:
            st.error("❌ No credentials found in secrets!")
            st.info("Please add 'gcp_service_account_json' to your Streamlit secrets.")
            return None
        
        # Create credentials object
        credentials = service_account.Credentials.from_service_account_info(
            credentials_dict,
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets.readonly",
                "https://www.googleapis.com/auth/drive.readonly"
            ]
        )
        
        # Build the service
        service = build('sheets', 'v4', credentials=credentials)
        return service
        
    except json.JSONDecodeError as e:
        st.error(f"❌ Error parsing JSON credentials: {str(e)}")
        st.info("Make sure your JSON is valid and properly formatted.")
        return None
        
    except Exception as e:
        st.error(f"❌ Error connecting to Google Sheets")
        st.error(f"Error details: {str(e)}")
        
        # Provide helpful debugging info
        with st.expander("🔍 Troubleshooting Help"):
            st.markdown("""
            **The EASIEST way to fix this:**
            
            Use the **JSON method**! Add this to your Streamlit secrets:
            
            ```toml
            gcp_service_account_json = '''
            PASTE YOUR ENTIRE JSON FILE CONTENT HERE
            '''
            ```
            
            **Check SECRETS_GUIDE.md for the complete format!**
            """)
        return None

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_sheet_data(sheet_id, range_name="Sheet1"):
    """Load data from Google Sheet"""
    try:
        service = get_google_sheets_client()
        if not service:
            return None
        
        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(
            spreadsheetId=sheet_id,
            range=range_name
        ).execute()
        
        values = result.get('values', [])
        
        if not values:
            st.warning("No data found in the sheet.")
            return None
        
        # Convert to DataFrame
        df = pd.DataFrame(values[1:], columns=values[0])
        return df
    
    except Exception as e:
        st.error(f"Error loading sheet data: {str(e)}")
        return None

def is_video_url(url):
    """Check if URL is a video based on extension"""
    video_extensions = ['.mp4', '.webm', '.mov', '.avi', '.mkv']
    return any(url.lower().endswith(ext) for ext in video_extensions)

def display_product(row, index):
    """Display a single product with its media and tags"""
    url = row.get('URL', '').strip()
    
    if not url:
        return
    
    with st.container():
        # Create columns for better layout
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Display media
            try:
                if is_video_url(url):
                    st.video(url)
                else:
                    st.image(url, use_container_width=True)
            except Exception as e:
                st.error(f"Error loading media: {str(e)}")
        
        with col2:
            # Display tags in organized sections
            st.markdown('<div class="tag-container">', unsafe_allow_html=True)
            
            # Kurdish Section
            st.markdown("### 🇮🇶 Kurdish")
            
            kurdish_tags = row.get('Kurdish Tags', '').strip()
            if kurdish_tags:
                st.markdown(f'<div class="tag-label">Tags:</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="tag-value">{kurdish_tags}</div>', unsafe_allow_html=True)
            
            kurdish_colors = row.get('Kurdish Color Tags', '').strip()
            if kurdish_colors:
                st.markdown(f'<div class="tag-label">Colors:</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="tag-value">{kurdish_colors}</div>', unsafe_allow_html=True)
            
            kurdish_materials = row.get('Kurdish Material Tags', '').strip()
            if kurdish_materials:
                st.markdown(f'<div class="tag-label">Materials:</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="tag-value">{kurdish_materials}</div>', unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Arabic Section
            st.markdown("### 🇸🇦 Arabic")
            
            arabic_tags = row.get('Arabic Tags', '').strip()
            if arabic_tags:
                st.markdown(f'<div class="tag-label">Tags:</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="tag-value">{arabic_tags}</div>', unsafe_allow_html=True)
            
            arabic_colors = row.get('Arabic Colors Tags', '').strip()
            if arabic_colors:
                st.markdown(f'<div class="tag-label">Colors:</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="tag-value">{arabic_colors}</div>', unsafe_allow_html=True)
            
            arabic_materials = row.get('Arabic Material Tags', '').strip()
            if arabic_materials:
                st.markdown(f'<div class="tag-label">Materials:</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="tag-value">{arabic_materials}</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")

def main():
    """Main application function"""
    
    # Header
    st.title("🛍️ Product Gallery")
    st.markdown("Browse our product collection with detailed information in Kurdish and Arabic")
    
    # Sidebar for settings
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Google Sheet ID input
        sheet_id = st.text_input(
            "Google Sheet ID",
            help="Enter the Google Sheet ID from the URL",
            placeholder="1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
        )
        
        # Sheet name input
        sheet_name = st.text_input(
            "Sheet Name",
            value="Sheet1",
            help="Enter the name of the sheet tab"
        )
        
        # Refresh button
        if st.button("🔄 Refresh Data"):
            st.cache_data.clear()
            st.rerun()
        
        st.markdown("---")
        st.markdown("**Note:** Data is cached for 5 minutes for optimal performance.")
    
    # Load and display data
    if sheet_id:
        with st.spinner("Loading products..."):
            df = load_sheet_data(sheet_id, sheet_name)
            
            if df is not None and not df.empty:
                st.success(f"✅ Loaded {len(df)} products")
                
                # Display products
                for index, row in df.iterrows():
                    display_product(row, index)
            else:
                st.info("👆 Please enter a valid Google Sheet ID in the sidebar")
    else:
        st.info("👆 Please enter your Google Sheet ID in the sidebar to get started")
        
        # Instructions
        with st.expander("📖 How to get your Google Sheet ID"):
            st.markdown("""
            1. Open your Google Sheet
            2. Look at the URL in your browser
            3. The Sheet ID is the long string between `/d/` and `/edit`
            
            **Example URL:**
            ```
            https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit
            ```
            
            **Sheet ID would be:**
            ```
            1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms
            ```
            """)

if __name__ == "__main__":
    main()
