# TransferDocs(Result Analysis)
Analysis of results of college students and determining the growth, decline and complete end to analysis of the results.


## 🚀 Features
- **Automated Extraction:** Parse academic data from uploaded documents.
- **Trend Detection:** Specifically designed to determine growth and decline patterns in student results.
- **Interactive UI:** A clean, user-friendly interface for uploading files and viewing analysis.
- **Performance Metrics:** Comprehensive breakdown of result statistics.

## 🛠️ Tech Stack
The Complete Tech Stack
1. Core Language & Environment
Python 3.10+: The backbone of both the backend and frontend.

Uvicorn: An ASGI web server implementation for Python, used to run the FastAPI backend.

2. Backend (API & Intelligence)
FastAPI: A high-performance web framework for building the APIs that handle file uploads, stats, and chat.

Google Gemini API (gemini-2.5-flash): ##Free tier API

OCR & Extraction: Converts complex PDF result gazettes into structured JSON.

NLP to Query: Converts user questions into executable MongoDB queries.

PyPDF2: Used for initial PDF processing, such as counting pages.

Pydantic: For data validation and settings management using Python type annotations.

3. Database (Persistence)
MongoDB: A NoSQL database used to store student records as flexible JSON-like documents.

PyMongo: The official Python driver for MongoDB.

4. Frontend (User Interface)
Streamlit: A powerful framework for creating the web interface with minimal effort.

Plotly Express: Used to create interactive, responsive charts (Pie charts for pass/fail and Histograms for CGPA).

Pandas: The industry-standard library for data manipulation, used here to format database results for the UI and charts.

Requests: Handles the communication between the Streamlit UI and the FastAPI backend.

5. Infrastructure & Utils
CORS Middleware: Configured in FastAPI to allow the frontend to communicate with the backend securely.

Shutil/OS: For local file system operations like managing the temp_uploads folder.

## 📁 Project Structure
- `frontend.py`: The entry point for the Streamlit application; manages user interactions and visualizations.
- `backend.py`: Contains the business logic, data parsing algorithms, and analysis functions.
- `temp_uploads/`: Secure directory for handling temporary session-based files.
- `.gitignore`: Configured to exclude temporary files and environment data from the repository.

## ⚙️ Setup and Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/sujxxll/TransferDocs.git](https://github.com/sujxxll/TransferDocs.git)
   cd TransferDocs

2. Set up a virtual environment:
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate

3. Install required dependencies:
(Ensure you have streamlit and pandas installed)
pip install streamlit pandas fastapi uvicorn google-generativeai pymongo PyPDF2 python-multipart plotly requests

4. Run Applications
Bash
python backend.py ##Run the server first.

Bash
streamlit run frontend.py ##Run the frontend for UI/UX

----------------------------------------------------------------------------------------------------------------------------

📊 Usage
Launch the app using the command above.

Upload the student result document (e.g., PDF or CSV).

The system will process the data through backend.py.

Review the generated analysis on the dashboard to see growth or decline indicators.
