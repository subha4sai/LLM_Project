from dotenv import load_dotenv
import streamlit as st
import os
import sqlite3
import smtplib
from email.mime.text import MIMEText
import google.generativeai as genai

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
def read_sql_query(sql, db):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    conn.commit()
    conn.close()
    return rows

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

# Define your prompt
prompt=[
    """
 
    You are an expert in converting English questions to SQL query!
    The SQL database has the name T_TE_SAMPLE_DATA and has the following columns - BUYER_CITY "Customer City", BUYER_GSTIN "Customer GSTIN", BUYER_PINCODE "Customer Pincode", SHIP_LOCATION "Shipping Location", SHIP_PINCODE "Shipping Pincode" ,HSN_CODE "HSN Code",
    quantity , SELLER_GSTIN "Seller GSTIN" , DOCTYPE "Invoice", DOCTYPE "Transactions", DOCNO "Invoice Number", DOCDATE "Invoice date", DOCDATE "Transaction date",
	SELLER_LEGALNAME "Selling Company" , SELLER_ADDRESS1 "Seller Address" , SELLER_ADDRESS2 "Seller Location", SELLER_CITY "Seller Location" , SELLER_PINCODE "Seller Pincode", SELLER_STATECODE "Seller State code" , BUYER_GSTIN "Buyer GSTIN" , BUYER_LEGALNAME "Customer Name", BUYER_ADDRESS1 "Customer Address", BUYER_ADDRESS2 "Customer Location" , BUYER_CITY "Customer City",
	BUYER_PINCODE "Customer Pincode", BUYER_STATECODE "Customer State code" , SHIP_GSTIN "Ship to GSTIN" , SHIP_LEGALNAME "Ship to Party" , SHIP_ADDRESS1 "Ship to Location" , SHIP_ADDRESS2 "Ship to Address", SHIP_LOCATION "Ship Location" , SHIP_PINCODE "Ship to Pincode" , SHIP_STATECODE	"Ship to State Code",PRODUCT_DESCRIPTION "Product Name", USER_SP_PRICE "Price" , TOTAL_VAL "Line Total" , PRE_TAX_VALUE "Item Total", ASS_AMT "Tax Assessible Amount" , GST_RATE "GST Rate" , IGST_RATE "IGST Rate",
IGST_AMT "IGST Amount" , SGST_AMT "SGST Amount" , CGST_AMT "CGST Amount" \n
\nFor example,
    \nExample 1 - List invoices for SELLER_LEGALNAME?,
    the SQL command will be something like this SELECT * FROM T_TE_SAMPLE_DATA WHERE SELLER_LEGALNAME='Vision power private Ltd.';
    the SQL command will be something like this SELECT * FROM T_TE_SAMPLE_DATA INVOICES WHERE SELLER_LEGALNAME='Vision power private Ltd.';
    the SQL command will be something like this SELECT * FROM T_TE_SAMPLE_DATA TRANSACTIONS WHERE SELLER_LEGALNAME='Vision power private Ltd.';
    \nExample 2 - How many entries of records are present?,
    the SQL command will be something like this SELECT COUNT(*) FROM T_TE_SAMPLE_DATA where seller_legalname like 'Vision power private %' ;
    \nExample 3 - Tell me the all product information based on buyer city?,
    the  SQL command will be something like this SELECT BUYER_LEGALNAME,
	BUYER_CITY,SELLER_LEGALNAME,
	SELLER_CITY,HSN_CODE AS PRODUCT,PRODUCT_DESCRIPTION,	
	QUANTITY,
	USER_SP_PRICE,
	TOTAL_VAL,
	DISCOUNT FROM T_TE_SAMPLE_DATA WHERE BUYER_CITY = "HYDERABAD";
    \nExample 4- Tell me the all product information based on buyer city and seller city?,
    the  SQL command will be something like this SELECT BUYER_LEGALNAME AS CUSTOMER,
	BUYER_CITY,SELLER_LEGALNAME AS VENDOR,
	SELLER_CITY,HSN_CODE AS PRODUCT,PRODUCT_DESCRIPTION,	
	QUANTITY,
	USER_SP_PRICE,
	TOTAL_VAL,
	DISCOUNT FROM T_TE_SAMPLE_DATA WHERE BUYER_CITY = "HYDERABAD" AND SELLER_CITY = "VIJAYAWADA";
    \nExample 5- Tell me the customer info of buying a particular product from a particular location?,
    the  SQL command will be something like this SELECT BUYER_LEGALNAME,
	BUYER_CITY,SELLER_LEGALNAME,
	SELLER_CITY,HSN_CODE AS PRODUCT,PRODUCT_DESCRIPTION,	
	QUANTITY,
	USER_SP_PRICE,
	TOTAL_VAL,
	DISCOUNT FROM T_TE_SAMPLE_DATA WHERE BUYER_CITY = "HYDERABAD" AND PRODUCT = 68114075;
    \nExample 6- Tell me the top sellers of a particular product based on a particular city?,
    the  SQL command will be something like this SELECT SUM(TOTAL_VAL) AS TOTAL_VAL,SELLER_LEGALNAME,HSN_CODE AS PRODUCT,PRODUCT_DESCRIPTION FROM T_TE_SAMPLE_DATA GROUP BY SELLER_LEGALNAME,PRODUCT;	 
    \nExample 7 - List all CGST and SGST amount or sum(TAX_AMOUT)?,
    the SQL command will be somthing like this SELECT * FROM T_TE_SAMPLE_DATA WHERE SELLER_LEGALNAME='Vision power private Ltd.';
    \nExample 8 - Tell me the total tax amount based on the city?,
    the SQL command will be somthing like this SELECT SUM(SGST_AMT), SUM(CGST_AMT),SUM(SGST_AMT +CGST_AMT) AS TAX_AMOUNT,BUYER_CITY FROM T_TE_SAMPLE_DATA  GROUP BY BUYER_CITY HAVING COUNT(*) <= 10;
    \nExample 9 - display number of invoices for buyer like Advantage Buying ?,
    the SQL command will be somthing like this SELECT count(*) FROM T_TE_SAMPLE_DATA WHERE BUYER_LEGALNAME LIKE "Advantage%";
    also the sql code should not have ''' in beginning or end and sql word in output
    \nExample 10 - display number of Interstate Invoices for buyer like Advantage Buying ?,
    the SQL command will be something like this SELECT count(*) FROM T_TE_SAMPLE_DATA WHERE SELLER_STATECODE = BUYER_STATECODE and BUYER_LEGALNAME LIKE "Advantage%";
    \nExample 11 - display number of Intrastate Invoices for buyer like Advantage Buying ?,
    the SQL command will be something like this SELECT count(*) FROM T_TE_SAMPLE_DATA WHERE SELLER_STATECODE <> BUYER_STATECODE and BUYER_LEGALNAME LIKE "Advantage%";
    \nExample 12 - display the IGST TOTAL Amount for Intrastate Invoices for buyer like Advantage Buying ?,
    the SQL command will be something like this SELECT sum(IGST_AMT) FROM T_TE_SAMPLE_DATA WHERE SELLER_STATECODE <> BUYER_STATECODE and BUYER_LEGALNAME LIKE "Advantage%";
 \nExample 13 - display the SGST/CGST TOTAL Amount for Interstate Invoices for buyer like Advantage Buying ?,
    the SQL command will be something like this SELECT sum(CGST_AMT)+Sum(SGST_AMT) FROM T_TE_SAMPLE_DATA WHERE SELLER_STATECODE = BUYER_STATECODE and BUYER_LEGALNAME LIKE "Advantage%";
 \nExample 14 - display the state wise SGST/CGST TOTAL Amount for Intrastate Invoices for buyer like Advantage Buying ?,
    the SQL command will be something like this SELECT sum(CGST_AMT)+Sum(SGST_AMT) , BUYER_STATECODE FROM T_TE_SAMPLE_DATA WHERE SELLER_STATECODE = BUYER_STATECODE and BUYER_LEGALNAME LIKE "Advantage%" GROUP BY BUYER_STATECODE; 
 \nExample 15 - display the state wise IGST TOTAL Amount for Interstate Invoices for buyer like Advantage Buying ?,
    the SQL command will be something like this SELECT sum(IGST_AMT) , BUYER_STATECODE FROM T_TE_SAMPLE_DATA WHERE SELLER_STATECODE <> BUYER_STATECODE and BUYER_LEGALNAME LIKE "Advantage%" GROUP BY BUYER_STATECODE; 
 \nExample 16 - display the TOTAL igst TAX AMOUNT with statewise breakup for buyer like Advantage Buying ?,
    the SQL command will be something like this SELECT sum(IGST_AMT) , BUYER_STATECODE FROM T_TE_SAMPLE_DATA  WHERE SELLER_STATECODE <> BUYER_STATECODE and BUYER_LEGALNAME LIKE "Advantage%" GROUP BY BUYER_STATECODE ; 
\nExample 17 - display the TOTAL GST AMOUNT for each buyer or gst amount paid by each buyer?,
    the SQL command will be something like this SELECT BUYER_LEGALNAME,SUM(CGST_AMT + SGST_AMT) AS TOTAL_GST_AMT FROM T_TE_SAMPLE_DATA GROUP BY BUYER_LEGALNAME ; 
    also the sql code should not have ''' in beginning or end and sql word in output

    
 """
 
]

# Streamlit App
st.set_page_config(page_title="I can Retrieve Any SQL query")
st.header("Trans AI To Retrieve SQL Data")

# Initialize session state for query and email status
if 'query' not in st.session_state:
    st.session_state.query = ""
if 'response_text' not in st.session_state:
    st.session_state.response_text = ""
if 'email_status' not in st.session_state:
    st.session_state.email_status = ""
###############################################
col1, col2 = st.columns(2)

with col1:
    st.header('Retrieve SQL Data')
    question = st.text_input("Input: ", key="input")
    submit = st.button('Ask the question')


###############################################
# Input for question
#question = st.text_input("Input: ", key="input")
#submit = st.button("Ask the question")

# If submit is clicked
if submit:
    sql_query = get_gemini_response(question, prompt)
    st.session_state.query = sql_query
    # st.write(f"Generated SQL Query: {sql_query}")
    
    if sql_query:
        response = read_sql_query(sql_query, "D_TE_SAMPLE.db")
        st.session_state.response_text = "\n".join([str(row) for row in response])
        st.subheader("The Response is:")
        st.write(st.session_state.response_text)

# Email sending section
#email_sender = st.text_input('From')
with col2:
    st.header(' ')
    email_receiver = st.text_input('Receiver Email')
    #subject = st.text_input('Subject')
    send = st.button('Send Response as Email')
#password = st.text_input('Password', type="password") 6

if send:
    st.write(st.session_state.response_text)
    if st.session_state.response_text:
        email_body = f"Here is the result of your SQL query:\n\n{st.session_state.response_text}"
        st.session_state.email_status = send_email('bhavyaainapure@gmail.com', 'qqrc msyy lndf fzjk', email_receiver, question, email_body)
        if 'Email sent successfully!' in st.session_state.email_status:
            st.success(st.session_state.email_status)
        else:
            st.error(st.session_state.email_status)
    else:
        st.error("No data to send. Please query the database first.")