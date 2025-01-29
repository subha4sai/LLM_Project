from dotenv import load_dotenv
import streamlit as st
import os
from email.mime.text import MIMEText
import google.generativeai as genai
import cx_Oracle
import pandas as pd
import smtplib

# Load environment variables
load_dotenv()
# Set page configuration
st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(
    """
    <style>
    /* Change background color to black */
    .main {
        background-color: #6666ff;
    }

    /* Change text color to white */
    body, p, h1, h2, h3, h4, h5, h6, .stTextInput, .stButton button {
        color: white;
    }

    /* Change sidebar background color to black */
    .css-1d391kg, .css-1d391kg {
        background-color: #000000;
    }

    /* Change sidebar text color to white */
    .css-1d391kg, .css-1d391kg h2 {
        color: white;
    }

    /* Change input box and button styles */
    .stTextInput > div > input, .stButton > button {
        background-color: #333333;
        color: white;
        border-color: #444444;
    }

    .stTextInput > div > input::placeholder {
        color: #888888;
    }

    .stButton > button:hover {
        background-color: #444444;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)
st.image('https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQtI-o1YZ0wYe-meYAuuL7f8xfjAkKS-Zr_lg&s', width=200) 
st.title("Welcome to Trans AI ")
st.write("Hello")


# Google Gemini API configuration
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to get response from Google Gemini model
def get_gemini_response(question, prompt):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content([prompt[0], question])
    return response.text

# Function to execute an SQL query on an Oracle database
def read_sql_query(sql, user, password, dsn, encoding="UTF-8"):
    conn = cx_Oracle.connect(user=user, password=password, dsn=dsn, encoding=encoding)
    df = pd.read_sql(sql, conn)
    conn.close()
    return df

# Function to send an email
def send_email(sender, password, receiver, subject, body):
    try:
        msg = MIMEText(body)
        msg['From'] = sender
        msg['To'] = receiver
        msg['Subject'] = subject

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, receiver, msg.as_string())
        server.quit()

        return 'Email sent successfully! 🚀'
    except Exception as e:
        return f"Error occurred while sending the email: {e}"
    
prompt=[
    """
    You are an expert in converting English questions to Oracle SQL query!
    The Oracle SQL database has the name TE_Sample_Data and has the following columns - BUYER_CITY "Customer City", BUYER_GSTIN "Customer GSTIN", BUYER_PINCODE "Customer Pincode", SHIP_LOCATION "Shipping Location", SHIP_PINCODE "Shipping Pincode", HSN_CODE "HSN Code",
    quantity , SELLER_GSTIN "Seller GSTIN" , DOCTYPE "Invoice", DOCTYPE "Transactions", DOCNO "Invoice Number", DOCDATE "Invoice date", DOCDATE "Transaction date",
    SELLER_LEGALNAME "Selling Company" , SELLER_ADDRESS1 "Seller Address" , SELLER_ADDRESS2 "Seller Location", SELLER_CITY "Seller Location" , SELLER_PINCODE "Seller Pincode", SELLER_STATECODE "Seller State code" , BUYER_GSTIN "Buyer GSTIN" , BUYER_LEGALNAME "Customer Name", BUYER_ADDRESS1 "Customer Address", BUYER_ADDRESS2 "Customer Location" , BUYER_CITY "Customer City",
    BUYER_PINCODE "Customer Pincode", BUYER_STATECODE "Customer State code" , SHIP_GSTIN "Ship to GSTIN" , SHIP_LEGALNAME "Ship to Party" , SHIP_ADDRESS1 "Ship to Location" , SHIP_ADDRESS2 "Ship to Address", SHIP_LOCATION "Ship Location" , SHIP_PINCODE "Ship to Pincode" , SHIP_STATECODE "Ship to State Code",PRODUCT_DESCRIPTION "Product Name", USER_SP_PRICE "Price" , TOTAL_VAL "Line Total" , PRE_TAX_VALUE "Item Total", ASS_AMT "Tax Assessible Amount" , GST_RATE "GST Rate" , IGST_RATE "IGST Rate",
    IGST_AMT "IGST Amount" , SGST_AMT "SGST Amount" , CGST_AMT "CGST Amount" \n
    \nFor example,
    	The connected database have a table name like xx_sample_data with the following columns of BUYER_CITY, BUYER_GSTIN, BUYER_PINCODE,	SHIP_LOCATION, SHIP_PINCODE, HSN_CODE, quantity, SELLER_GSTIN,DOCTYPE,
		DOCNO, DOCDATE, SELLER_LEGALNAME, SELLER_ADDRESS1, SELLER_ADDRESS2,	SELLER_CITY,SELLER_PINCODE, SELLER_STATECODE,
		BUYER_LEGALNAME, BUYER_ADDRESS1,BUYER_ADDRESS2,BUYER_STATECODE,SHIP_GSTIN,SHIP_LEGALNAME,SHIP_ADDRESS1,SHIP_ADDRESS2,
        SHIP_STATECODE,PRODUCT_DESCRIPTION,USER_SP_PRICE,TOTAL_VAL,PRE_TAX_VALUE,ASS_AMT,GST_RATE,IGST_RATE,IGST_AMT,SGST_AMT,CGST_AMT it gives the my transaction information
    \nExample 1 - Total Number of Transaction?,
    the SQL command will be something like this SELECT * FROM TE_Sample_Data where BUYER_LEGALNAME = 'SmartBuy Network';
    \nExample 2 - display the month and year of maximum total amount of top 10 for each buyer ,
    the SQL command will be something like this select  distinct buyer_legalname, Sum(total_val) as Total_amount , to_char(docdate,'Month') as Month ,to_char(docdate,'YYYY') as Year
    from TE_Sample_Data where ROWNUM <> 10 GROUP BY docdate,buyer_legalname,total_val;
    \n
    The SQL code should not have ''' in beginning or end and SQL keyword in output.
    and it should be in the right oracle SQL syntax and if in the oracle SQL script have extra ; in the end remove it
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
col1, col2, col3 = st.columns(3)

# Retrieve SQL Data
with col2:
    st.header('Retrieve SQL Data')
    question = st.text_input("Enter your question:", key="input")
    submit = st.button('Ask the question')

# Oracle database credentials
user = "SYSTEM"
password = "oracle"
dsn = "localhost:1521/xepdb1"

# Generate and execute SQL query on submit
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

# Plotting the area chart
with col1:
    col1, col2 = st.columns(2)
    if st.session_state.df is not None and not st.session_state.df.empty:
        try:
            with col1:
                x_column = st.selectbox("Select the x-axis column", st.session_state.df.columns)
            with col2:
                y_columns = st.selectbox("Select the y-axis column(s)", st.session_state.df.columns)

            if x_column and y_columns:
                st.area_chart(
                data=st.session_state.df.set_index(x_column)[y_columns],
                use_container_width=True)
        
        except Exception as e:
                st.error(f"Please Select the Different Combination for generate Charts")
        
# Email sending section
with col3:
    st.header(' ')
    email_receiver = st.text_input('Receiver Email')
    send = st.button('Send Response as Email')

if send:
    if st.session_state.response_text:
        email_body = f"Here is the result of your SQL query:\n\n{st.session_state.response_text}"
        st.session_state.email_status = send_email(
            'subhashini.s@transformedge.com',
            '',  # Use a secure method for storing and retrieving the email password
            email_receiver,
            question,
            email_body
        )
        if 'Email sent successfully!' in st.session_state.email_status:
            st.success(st.session_state.email_status)
        else:
            st.error(st.session_state.email_status)
    else:
        st.error("No data to send. Please query the database first.")
