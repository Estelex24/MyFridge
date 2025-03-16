import streamlit as st
import pandas as pd
from supabase import create_client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set page configuration
st.set_page_config(page_title="Supabase Demo", layout="wide")

# App title and description
st.title("Streamlit + Supabase Integration Demo")
st.markdown("This app demonstrates how to connect Streamlit with Supabase for data management.")

# Initialize connection to Supabase
@st.cache_resource
def init_connection():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        st.error("Supabase credentials not found. Please set SUPABASE_URL and SUPABASE_KEY in your .env file.")
        st.stop()
    
    return create_client(url, key)

# Attempt to connect to Supabase
try:
    supabase = init_connection()
    st.success("Connected to Supabase successfully!")
except Exception as e:
    st.error(f"Failed to connect to Supabase: {str(e)}")
    st.stop()

# Create a sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Choose a page", ["View Data", "Add Data", "Search Data"])

# Function to fetch data from a table
def fetch_data(table_name):
    response = supabase.table(table_name).select("*").execute()
    return pd.DataFrame(response.data)

# Function to insert data into a table
def insert_data(table_name, data_dict):
    response = supabase.table(table_name).insert(data_dict).execute()
    return response

# Define table name
table_name = "demo_table"  # Change this to your actual table name

# Page: View Data
if page == "View Data":
    st.header("View Data")
    
    try:
        # Fetch and display data
        data = fetch_data(table_name)
        
        if data.empty:
            st.info(f"No data found in the {table_name} table.")
        else:
            st.dataframe(data)
            
            # Download option
            csv = data.to_csv(index=False)
            st.download_button(
                label="Download as CSV",
                data=csv,
                file_name=f"{table_name}.csv",
                mime="text/csv"
            )
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")

# Page: Add Data
elif page == "Add Data":
    st.header("Add New Data")
    
    # For simplicity, assuming the table has 'name' and 'description' columns
    # Modify these fields according to your actual table structure
    with st.form("add_data_form"):
        name = st.text_input("Name")
        description = st.text_area("Description")
        
        submitted = st.form_submit_button("Submit")
        
        if submitted:
            if name:
                try:
                    # Insert new data
                    data = {"name": name, "description": description}
                    response = insert_data(table_name, data)
                    
                    st.success("Data added successfully!")
                    st.write(response)
                except Exception as e:
                    st.error(f"Error adding data: {str(e)}")
            else:
                st.warning("Name is required.")

# Page: Search Data
elif page == "Search Data":
    st.header("Search Data")
    
    search_term = st.text_input("Search by name")
    
    if search_term:
        try:
            # Search for data
            response = (
                supabase.table(table_name)
                .select("*")
                .ilike("name", f"%{search_term}%")
                .execute()
            )
            
            results = pd.DataFrame(response.data)
            
            if results.empty:
                st.info(f"No results found for '{search_term}'.")
            else:
                st.dataframe(results)
        except Exception as e:
            st.error(f"Error searching data: {str(e)}")

# Add some info about the app
st.sidebar.markdown("---")
st.sidebar.info(
    """
    This is a simple demo showing how to connect Streamlit with Supabase.
    
    Make sure to set up your .env file with your Supabase credentials.
    """
)
