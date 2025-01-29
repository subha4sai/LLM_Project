from turtle import goto
from dotenv import load_dotenv
import streamlit as st
import os
import cx_Oracle
import pandas as pd
import altair as alt
import google.generativeai as genai
import folium




# Set up the page configuration
st.set_page_config(
    page_title="Gemini SQL Query App",
    page_icon="🏂",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.markdown(
    """
    <style>
    .main {
        background-color: #6666ff;
    }
    body, p, h1, h3, h4, h5, h6, .stTextInput, .stButton button {
        color: black;
    }
    
    h2{
    color: white
    }

    .css-1d391kg {
        background-color: #223bdd;
    }
    .css-1d391kg h2 {
        color: Black;
    }
    .stTextInput > div > input, .stButton > button {
        background-color: #333333;
        color: white;
        border-color: #444444;
    }

        .css-1d391kg .css-1siy2t0 {
        color: #333333;
    }
    .css-1d391kg .stTextInput > div > input::placeholder {
        color: #888888;
    }
    .css-1d391kg .css-1coo3d2 {
        background-color: #e0e0e0;
    }
    .stButton > button:hover {
        background-color: #444444;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Sidebar for input
with st.sidebar:
    st.title('Navigation Menu')
    
    # Database Credentials
    st.subheader("Database Credentials")
    user = st.text_input("DB User", "SYSTEM")
    password = st.text_input("DB Password", "oracle", type="password")
    dsn = st.text_input("DSN", "localhost:1521/xepdb1")
    
    # Query Input
    st.subheader("Query Input")
    question = st.text_input("Enter your question:", key="input")
    submit = st.button('Ask the question')

# Load environment variables
load_dotenv()

# Configure Google Gemini AI API Key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to get response from Google Gemini model
def get_gemini_response(question, prompt):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content([prompt[0], question])
    return response.text

# Function to retrieve query from the database
def read_sql_query(sql, user, password, dsn, encoding="UTF-8"):
    conn = cx_Oracle.connect(user=user, password=password, dsn=dsn, encoding=encoding)
    df = pd.read_sql(sql, conn)
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    conn.commit()
    conn.close()
    return df

# Define your prompt
prompt=[
    """You are a very intelligent AI assistant who is an expert in identifying relevant questions from users and converting them into SQL queries to generate correct answers.
Please use the below context to write the Oracle SQL queries. Do not use MySQL queries.
Context:
You must query against the connected database, which has 1 table, TE_SAMPLE_DATA.
TE_SAMPLE_DATA has columns: TRX_ID, DOCTYPE, DOCNO, DOCDATE, SELLER_GSTIN, SELLER_LEGALNAME, SELLER_ADDRESS1, SELLER_ADDRESS2, SELLER_CITY, SELLER_PINCODE, SELLER_STATECODE, BUYER_GSTIN, BUYER_LEGALNAME, BUYER_ADDRESS1, BUYER_ADDRESS2, BUYER_CITY, BUYER_PINCODE, BUYER_STATECODE, BUYER_POST, SHIP_GSTIN, SHIP_LEGALNAME, SHIP_ADDRESS1, SHIP_ADDRESS2, SHIP_LOCATION, SHIP_PINCODE, SHIP_STATECODE, S_NO, PRODUCT_DESCRIPTION, IS_SERVICE, HSN_CODE, QUANTITY, FREEQTY, USER_SP_PRICE, TOTAL_VAL, DISCOUNT, PRE_TAX_VALUE, ASS_AMT, GST_RATE, IGST_RATE, IGST_AMT, SGST_AMT, CGST_AMT, ORDER_LINE_REF.
It gives the Sales information.
As an expert, you must use joins whenever required.
When a question involves summarizing or aggregating data, such as finding totals or averages by specific categories, you should use the SQL `GROUP BY` clause. For example, if a user asks for the total sales amount by product, your SQL query should group results by the `PRODUCT_DESCRIPTION` column and aggregate the `TOTAL_VAL` column.
if input is Month or year or Date you can take Docdate and extract the data.
when a question requires sorting data based on one or more columns, use the `ORDER BY` clause in your SQL query. For instance, if the user asks to see sales data ordered by date, you should sort the results by the `DOCDATE` column.
Also, the SQL code should not have ''' in the beginning or end and should not include the word SQL in the output.
it should be in the right oracle SQL syntax and if in the oracle SQL script have extra ; in the end remove it 
"""
]


if 'query' not in st.session_state:
    st.session_state.query = ""
if 'response_text' not in st.session_state:
    st.session_state.response_text = ""
if 'email_status' not in st.session_state:
    st.session_state.email_status = ""
if 'df' not in st.session_state:
    st.session_state.df = None

# Set up layout columns
col1, col2 = st.columns(2)  # Adjust column widths as needed

# Retrieve SQL Data
with col1:
    # st.header('Ask to AI')
    if submit and question:
        sql_query = get_gemini_response(question, prompt)
        st.session_state.query = sql_query.strip(";'")

        try:
            st.session_state.df = read_sql_query(st.session_state.query, user, password, dsn)
            st.write("Data Retrieved from Database:")
            st.write(st.session_state.df)

            if not st.session_state.df.empty:
                st.session_state.response_text = st.session_state.df.to_string(index=False)
            else:
                st.write("No data available for visualization.")
        except Exception as e:
            st.error(f"An error occurred: {e}")

# Heatmap Visualization
with col2:
    st.header('Heatmap Visualization')
    if st.session_state.df is not None and not st.session_state.df.empty:
        try:
            hcol1, hcol2, hcol3 = st.columns(3)
            # Select x, y, and color columns for the heatmap
            with hcol1:
                x_column = st.selectbox("Select the x-axis column", st.session_state.df.columns)
            with hcol2:
                y_column = st.selectbox("Select the y-axis column", st.session_state.df.columns)
            with hcol3:
                color_column = st.selectbox("Select the color column", st.session_state.df.columns)

            if x_column and y_column and color_column:
                # Create the heatmap
                heatmap = alt.Chart(st.session_state.df).mark_rect().encode(
                    x=alt.X(f'{x_column}:O', axis=alt.Axis(title=x_column, titleFontSize=14, titlePadding=10)),
                    y=alt.Y(f'{y_column}:O', axis=alt.Axis(title=y_column, titleFontSize=14, titlePadding=10)),
                    color=alt.Color(f'{color_column}:Q', scale=alt.Scale(scheme='viridis'), legend=alt.Legend(title=color_column)),
                    tooltip=[x_column, y_column, color_column]
                ).properties(
                    width=400,
                    height=400
                )

                st.altair_chart(heatmap, use_container_width=True)

        except Exception as e:
            st.error(f"An error occurred while generating the heatmap: {e}")

# Donut Chart Visualization
with col1:
    st.header('Donut Chart Visualization')
    if st.session_state.df is not None and not st.session_state.df.empty:
        try:
            # Select the column for donut chart values
            dcol1, dcol2 = st.columns(2)
            with dcol1:
                value_column = st.selectbox("Select the column for values", st.session_state.df.columns)
            with dcol2:
                category_column = st.selectbox("Select the column for categories", st.session_state.df.columns)

            if value_column and category_column:
                # Prepare the data for the donut chart
                df_donut = st.session_state.df[[category_column, value_column]]
                df_donut = df_donut.groupby(category_column).sum().reset_index()
                df_donut[value_column] = df_donut[value_column] / df_donut[value_column].sum() * 100

                # Create the donut chart
                donut_chart = alt.Chart(df_donut).mark_arc(innerRadius=50).encode(
                    theta=alt.Theta(f'{value_column}:Q', stack=True),
                    color=alt.Color(f'{category_column}:N', legend=alt.Legend(title=category_column)),
                    tooltip=[category_column, value_column]
                ).properties(
                    width=400,
                    height=400
                )

                st.altair_chart(donut_chart, use_container_width=True)

        except Exception as e:
            st.error(f"An error occurred while generating the donut chart: {e}")
            

 # Bubble Chart Visualization
with col2:
    st.header('Bubble Chart Visualization')
    if st.session_state.df is not None and not st.session_state.df.empty:
        try:
            # Select the columns for the bubble chart
            x_column = st.selectbox("Select the x-axis column for bubbles", st.session_state.df.columns)
            y_column = st.selectbox("Select the y-axis column for bubbles", st.session_state.df.columns)
            size_column = st.selectbox("Select the size column for bubbles", st.session_state.df.columns)
            color_column = st.selectbox("Select the color column for bubbles", st.session_state.df.columns)

            if x_column and y_column and size_column and color_column:
                # Prepare the bubble chart
                bubble_chart = alt.Chart(st.session_state.df).mark_circle().encode(
                    x=alt.X(f'{x_column}:Q', axis=alt.Axis(title=x_column, titleFontSize=14, titlePadding=10)),
                    y=alt.Y(f'{y_column}:Q', axis=alt.Axis(title=y_column, titleFontSize=14, titlePadding=10)),
                    size=alt.Size(f'{size_column}:Q', scale=alt.Scale(range=[100, 1000]), legend=alt.Legend(title=size_column)),
                    color=alt.Color(f'{color_column}:N', legend=alt.Legend(title=color_column)),
                    tooltip=[x_column, y_column, size_column, color_column]
                ).properties(
                    width=400,
                    height=400
                ).interactive()

                st.altair_chart(bubble_chart, use_container_width=True)

        except Exception as e:
            st.error(f"An error occurred while generating the bubble chart: {e}")



# Scatter Chart Visualization
with col2:
    st.header('Scatter Chart Visualization')
    if st.session_state.df is not None and not st.session_state.df.empty:
        try:
            # Select columns for the scatter chart
            x_column = st.selectbox("Select the x-axis column for Scatter Chart", st.session_state.df.columns)
            y_column = st.selectbox("Select the y-axis column for Scatter Chart", st.session_state.df.columns)
            color_column = st.selectbox("Select the color column for Scatter Chart (optional)", st.session_state.df.columns, index=0)
            size_column = st.selectbox("Select the size column for Scatter Chart (optional)", st.session_state.df.columns, index=0)

            if x_column and y_column:
                # Create the scatter chart
                scatter_chart = alt.Chart(st.session_state.df).mark_point().encode(
                    x=alt.X(f'{x_column}:Q', title=x_column),
                    y=alt.Y(f'{y_column}:Q', title=y_column),
                    color=alt.Color(f'{color_column}:N', legend=alt.Legend(title=color_column)) if color_column else alt.value('blue'),
                    size=alt.Size(f'{size_column}:Q', legend=alt.Legend(title=size_column)) if size_column else alt.value(100),
                    tooltip=[x_column, y_column] + ([color_column] if color_column else []) + ([size_column] if size_column else [])
                ).properties(
                    title='Scatter Chart',
                    width=600,
                    height=400
                ).interactive()

                st.altair_chart(scatter_chart, use_container_width=True)

        except Exception as e:
            st.error(f"An error occurred while generating the scatter chart: {e}")
     
           


# Histogram Chart Visualization
with col1:
    st.header('Histogram Visualization')
    if st.session_state.df is not None and not st.session_state.df.empty:
        try:
            # Select the column for the histogram
            value_column = st.selectbox("Select the column for Histogram", st.session_state.df.columns)
            
            if value_column:
                # Create the histogram
                histogram = alt.Chart(st.session_state.df).mark_bar().encode(
                    alt.X(f'{value_column}:Q', bin=alt.Bin(maxbins=30), title=value_column),
                    alt.Y('count():Q', title='Count'),
                    tooltip=[alt.Tooltip('count():Q', title='Count')]
                ).properties(
                    title='Histogram',
                    width=600,
                    height=400
                ).interactive()

                st.altair_chart(histogram, use_container_width=True)

        except Exception as e:
            st.error(f"An error occurred while generating the histogram: {e}")
