import pytesseract
from pdf2image import convert_from_path
import pandas as pd
import json
import os
from difflib import SequenceMatcher
import streamlit as st
import tempfile
import requests
from db import Session, Order, OrderLineItem
from ollama import Client

# File paths for CSV exports
orders_path = "orders.csv"
order_lines_path = "order_line_items.csv"

# Initialize Ollama client
ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
ollama_client = Client(host=ollama_host)

# STEP 1: OCR - Extract text from PDF
def extract_text_from_pdf(pdf_path):
    images = convert_from_path(pdf_path)
    text = ""
    for image in images:
        text += pytesseract.image_to_string(image)
    return text.strip()

# STEP 2: Use Ollama for invoice extraction
def query_ollama_for_invoice_data(text, model='qwen2.5:7b'):
    prompt = f"""
You are an AI assistant extracting structured data from invoice text.

Here is the invoice text:
{text}

Extract the following details as JSON:
- order_id
- customer_name
- email
- phone
- items (list of objects with: product_id, title, quantity, unit_price, line_total)
- subtotal
- vat
- grand_total

Format example:
{{
  "order_id": "12345",
  "customer_name": "John Doe",
  "email": "john@example.com",
  "phone": "None",
  "items": [
    {{
      "product_id": "1234567890",
      "title": "Item Name",
      "quantity": 2,
      "unit_price": 5.99,
      "line_total": 11.98
    }}
  ],
  "subtotal": 11.98,
  "vat": 0.60,
  "grand_total": 12.58
}}
"""
    response = ollama_client.chat(model=model, messages=[{"role": "user", "content": prompt}])
    content = response['message']['content']

    if content.strip().startswith("```json"):
        content = content.strip().removeprefix("```json").removesuffix("```").strip()

    try:
        return json.loads(content)
    except Exception as e:
        print(f"❌ Failed to parse response: {e}")
        print("⚠️ Raw model output:")
        print(content)
        return None

# STEP 3: Process invoice and save to DB + CSV
def process_invoice(pdf_path):
    print(f"📥 Processing file: {pdf_path}", flush=True)
    session = Session()
    text = extract_text_from_pdf(pdf_path)
    data = query_ollama_for_invoice_data(text)
    summary = ""

    if data:
        exists = session.query(Order).filter_by(order_id=data['order_id']).first()
        if exists:
            summary = f"Duplicate invoice detected for Order ID: {data['order_id']}"
        else:
            total_qty = sum(item['quantity'] for item in data['items'])
            order = Order(
                order_id=data['order_id'],
                customer_name=data['customer_name'],
                email=data['email'],
                phone=data['phone'],
                total_qty=total_qty,
                subtotal=data['subtotal'],
                vat=data['vat'],
                grand_total=data['grand_total']
            )
            session.add(order)

            for item in data['items']:
                line = OrderLineItem(
                    order_id=data['order_id'],
                    product_id=item['product_id'],
                    title=item['title'],
                    product_qty=item['quantity'],
                    line_total=item['line_total']
                )
                session.add(line)

            session.commit()
            print(f"✅ Order {data['order_id']} inserted into MySQL database")

            # Export to CSV
            try:
                orders_df = pd.read_sql_table('orders', session.bind)
                order_lines_df = pd.read_sql_table('order_line_items', session.bind)

                print(f"📊 Fetched {len(orders_df)} orders and {len(order_lines_df)} line items from DB")

                if not orders_df.empty:
                    orders_df.to_csv(orders_path, index=False)
                    print(f"✅ Exported orders.csv with {len(orders_df)} rows")
                else:
                    print("⚠️ No data in 'orders' table to export")

                if not order_lines_df.empty:
                    order_lines_df.to_csv(order_lines_path, index=False)
                    print(f"✅ Exported order_line_items.csv with {len(order_lines_df)} rows")
                else:
                    print("⚠️ No data in 'order_line_items' table to export")

            except Exception as e:
                print(f"❌ Failed to export CSV files: {e}")

            summary = f"✅ Order {data['order_id']} processed successfully."
            return summary, data
    else:
        summary = "❌ Failed to process invoice."

    return summary, None

# STEP 4: Streamlit App
st.title("🧾 Invoice Uploader")
st.write("Upload invoice PDFs to extract and store invoice data in the MySQL database.")

uploaded_files = st.file_uploader("Drag and drop invoices here:", type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    for uploaded_file in uploaded_files:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name

        result_message, parsed_data = process_invoice(tmp_path)
        st.success(result_message)

        if parsed_data:
            st.subheader(f"Order Summary for Order ID: {parsed_data['order_id']}")
            st.json(parsed_data)

    st.success("📁 Synchronized orders.csv and order_line_items.csv with database")
    st.download_button("Download Orders CSV", data=open(orders_path).read(), file_name="orders.csv")
    st.download_button("Download Line Items CSV", data=open(order_lines_path).read(), file_name="order_line_items.csv")

# STEP 5: Chat Assistant with MCP tool support
st.markdown("---")
st.subheader("🤖 Chat with Local LLM (Data Assistant + MCP API)")
user_input = st.text_input("Ask something about orders or perform a database action:", key="chat_input")

if st.button("Send", key="send_btn") and user_input:
    chat_prompt = f"""
        You are a data analysis assistant with access to an MCP API.

        Available endpoints (you must choose one of these):
        GET     http://mcp:9000/orders
        GET     http://mcp:9000/order/{{order_id}}
        POST    http://mcp:9000/order
        PATCH   http://mcp:9000/order/{{order_id}}
        DELETE  http://mcp:9000/order/{{order_id}}

        When the user asks a question, respond ONLY with a tool-call JSON like:

        {{
        "method": "GET",
        "url": "http://mcp:9000/orders"
        }}

        Do NOT include .csv or made-up endpoints.

        User query: {user_input}
        """

    response = ollama_client.chat(model='qwen2.5:7b', messages=[{"role": "user", "content": chat_prompt}])
    content = response['message']['content']

    try:
        print("📡 Raw LLM tool call:", content)
        tool_call = json.loads(content)
        method = tool_call.get("method", "GET").upper()
        url = tool_call.get("url")
        payload = tool_call.get("payload", {})
        print("🔧 Parsed Tool Call →", method, url)

        if method == "GET":
            tool_response = requests.get(url).json()
        elif method == "POST":
            tool_response = requests.post(url, json=payload).json()
        elif method == "PATCH":
            tool_response = requests.patch(url, json=payload).json()
        elif method == "DELETE":
            tool_response = requests.delete(url).json()
        else:
            tool_response = {"error": "Unsupported method"}

        print("📦 Tool Response JSON:", json.dumps(tool_response, indent=2))
        st.markdown("### 🛠 MCP Tool Response")
        st.json(tool_response)

        interpretation_prompt = f"""
        You are a helpful assistant. Here is the result of a database tool call:

        {json.dumps(tool_response, indent=2)}

        Now, please answer the user's original query:
        {user_input}

        Be precise, avoid guessing, and base your answer only on the data above.
        """

        print("🧠 Sending interpretation prompt:")
        print(interpretation_prompt)

        followup = ollama_client.chat(
            model='qwen2.5:7b',
            messages=[{"role": "user", "content": interpretation_prompt}]
        )

        print("💬 Final LLM Answer:", followup['message']['content'])
        st.markdown("### 🤖 Final Answer")
        st.markdown(followup['message']['content'])

    except Exception as e:
        print("❌ Exception during LLM+Tool handling:", e)
        st.markdown("### 🤖 LLM Response")
        st.markdown(content)
