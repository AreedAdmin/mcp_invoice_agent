# 🧾 Invoice Agent

**Invoice Agent** is a full-stack, containerized web application that uses OCR, LLMs, and FastAPI to extract, analyze, and manage invoice data.

---

## 🚀 Features

- 📥 **Invoice Upload**: Drag and drop PDFs to extract structured invoice data.
- 🔍 **OCR & Extraction**: Uses Tesseract + PDF-to-image + LLM (Ollama + Qwen2) to parse invoice text.
- 🧠 **LLM-Powered Analysis**: A Streamlit chatbot uses your local LLM to answer queries about orders.
- 📊 **Database & CSV Sync**: Automatically stores data in MySQL and syncs with local CSV files.
- 🧰 **MCP Tooling API**: A FastAPI server allows external agents (like the LLM) to view, edit, delete, and query orders.
- 📦 **Dockerized**: Runs with a single `docker-compose up`, including MySQL, Adminer, Streamlit, and MCP.

---

## 📂 Tech Stack

| Layer           | Tech                          |
|----------------|-------------------------------|
| UI             | Streamlit                     |
| OCR            | Tesseract, pdf2image          |
| LLM            | Ollama + Qwen2.5 7B (local)   |
| DB             | MySQL + SQLAlchemy            |
| Agent Server   | FastAPI (MCP)                 |
| CSV Output     | Pandas                        |
| Deployment     | Docker + Docker Compose       |

---

## 🛠 Setup Instructions

### 1. Clone the Repo
```bash
git clone https://github.com/YOUR_USERNAME/invoice-agent.git
cd invoice-agent
```

### 2. Start the Containers
```bash
docker-compose up --build
```

> This will launch:
> - 🐳 MySQL on port `3306`
> - 🖥 Adminer UI on `http://localhost:8080`
> - 📋 Streamlit UI on `http://localhost:8501`
> - 🧠 MCP Server API on `http://localhost:9000`

### 3. Access Ollama
Ensure Ollama is running on your **host machine**:
```bash
ollama serve
ollama run qwen2:7b
```

### 4. Use the App
- Open [http://localhost:8501](http://localhost:8501)
- Upload PDF invoices
- Chat with the LLM in natural language
- View database with Adminer ([http://localhost:8080](http://localhost:8080))

---

## 🔌 API Endpoints (MCP)

| Method | Endpoint                        | Description             |
|--------|----------------------------------|-------------------------|
| GET    | `/orders`                        | List all orders         |
| GET    | `/order/{order_id}`             | Get single order        |
| POST   | `/order`                         | Add new order           |
| PATCH  | `/order/{order_id}`             | Update existing order   |
| DELETE | `/order/{order_id}`             | Delete an order         |

The LLM will automatically call these endpoints when you ask questions like:
> "How many orders are in the database?"

---

## 📁 Project Structure
```
invoice_wrapper/
├── invoices/               # PDF uploads
├── Dockerfile              # Streamlit container
├── docker-compose.yaml     # All services
├── invoice_processor.py    # Main Streamlit app
├── mcp_server.py           # FastAPI MCP
├── db.py                   # SQLAlchemy models
├── requirements.txt        # Python deps
├── orders.csv              # Exported order rows
├── order_line_items.csv    # Exported item rows
```

---

## 📌 Environment Variables

Add these to your `.env` (auto loaded via Docker Compose):
```
DB_HOST=mysql
DB_USER=invoice_user
DB_PASS=invoice_pass
DB_NAME=invoice_db
OLLAMA_HOST=http://host.docker.internal:11434
```

---

## 📃 Example Prompt
Try in the chatbot:
> "List all customers who have ordered more than 5 items."

> "Delete the order with ID 0007."

> "How many invoices were uploaded this month?"

---

## 🧠 LLM Model
This project uses:
- `qwen2.5:7b` (or any local Ollama-compatible model)

You can replace this with `mistral`, `gemma`, or any model that supports reasoning and JSON output.

---

## 🔐 Security & Notes
- You should secure your FastAPI endpoints with auth tokens for production.
- Adminer should not be exposed on public ports.
- This is designed for **internal use** (staff uploading + auditing invoices).

---

## 💬 Contact & License
**Author:** Shehab
**License:** MIT  
Built using Ollama, FastAPI, Streamlit & Docker

