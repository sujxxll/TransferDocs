# TransferDocs(Result Analysis)
Analysis of results of college students and determining the growth, decline and complete end to analysis of the results.


## 🚀 Features
- **Automated Extraction:** Parse academic data from uploaded documents.
- **Trend Detection:** Specifically designed to determine growth and decline patterns in student results.
- **Interactive UI:** A clean, user-friendly interface for uploading files and viewing analysis.
- **Performance Metrics:** Comprehensive breakdown of result statistics.

## 🛠️ Tech Stack
- **Python:** Core programming language.
- **Streamlit:** Powers the frontend web interface.
- **Pandas:** Used for data manipulation and result analysis.
- **File Handling:** Logic for managing temporary file uploads and processing.

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
