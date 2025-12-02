import google.generativeai as genai
from pymongo import MongoClient
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import json
import os
import time
import PyPDF2
import shutil

# --- CONFIGURATION ---
# ⚠️ REPLACE WITH YOUR NEW, SECURE KEY
GEMINI_API_KEY = "AIzaSyAol1AnWmQYtZANOub5jm1TcA9R11cOg-c" 

MONGO_CONNECTION_STRING = "mongodb://localhost:27017/a"
MONGO_DB_NAME = "student_results_db"
MONGO_COLLECTION_NAME = "results"
TEMP_DIR = "temp_uploads"
os.makedirs(TEMP_DIR, exist_ok=True)

# --- INITIALIZE ---
try:
    genai.configure(api_key=GEMINI_API_KEY)
    # Using Flash for speed/context window
    llm = genai.GenerativeModel('gemini-2.5-flash') 
except Exception as e:
    exit(f"Error configuring Gemini API: {e}")

app = FastAPI(title="Student Analytics Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB Connection
client = MongoClient(MONGO_CONNECTION_STRING)
db = client[MONGO_DB_NAME]
collection = db[MONGO_COLLECTION_NAME]

# --- HELPER FUNCTIONS ---
def get_pdf_page_count(pdf_path):
    try:
        with open(pdf_path, 'rb') as f:
            return len(PyPDF2.PdfReader(f).pages)
    except: return 0

def upload_to_gemini(path, mime_type="application/pdf"):
    file = genai.upload_file(path, mime_type=mime_type)
    print(f"Uploaded file '{file.display_name}' as: {file.uri}")
    return file

def extract_data_from_page(file_ref, page_num):
    """
    Extracts FULL details including subject-wise breakdown.
    """
    prompt = f"""
    You are a precise Data Extraction AI. Extract the result table from PAGE {page_num} of this PDF.
    
    output must be a JSON LIST of student objects.
    
    **Extraction Rules:**
    1. **Basic Info:** Extract "Seat_No", "Name" (Name of Candidate), "Grand_Total" (e.g. 425), "CGPA", "Remark" (Pass/Fail), "SGPA_I", "SGPA_II".
    2. **Subjects (Crucial):** Look at the Table Header to identify Subject Names/Codes (e.g., "ITH-100", "SHM-133", "AEC-153", etc.).
       - Create a list called "Subjects" for each student.
       - Inside "Subjects", create an object for each column with:
         - "Name": The Subject Code/Name from the header.
         - "Total": The 'tot' marks obtained (integer).
         - "Grade": The 'LG' (Letter Grade) obtained.
         - "GP": The 'GP' (Grade Point).
    
    **JSON Structure Example:**
    [
      {{
        "Seat_No": "2524001",
        "Name": "AARON JESUS COSTA",
        "Grand_Total": 400,
        "SGPA_I": 6.85,
        "CGPA": 7.00,
        "Remark": "PASSES",
        "Subjects": [
           {{ "Name": "ITH-100 Python", "Total": 45, "Grade": "C", "GP": 5 }},
           {{ "Name": "SHM-133 Physics", "Total": 22, "Grade": "A", "GP": 8 }}
        ]
      }}
    ]

    Return ONLY raw JSON. If the page has no student rows, return [].
    """
    try:
        response = llm.generate_content([file_ref, prompt])
        text = response.text.strip()
        
        # Clean up JSON markdown
        if text.startswith("```json"): text = text[7:]
        if text.startswith("```"): text = text[3:]
        if text.endswith("```"): text = text[:-3]
        text = text.strip()
        
        # Parse
        data = json.loads(text)
        return data if isinstance(data, list) else []
    except Exception as e:
        print(f"Error parsing page {page_num}: {e}")
        return []

# --- ROUTES ---

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    file_path = os.path.join(TEMP_DIR, file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    try:
        gemini_file = upload_to_gemini(file_path)
        page_count = get_pdf_page_count(file_path)
        
        all_data = []
        # Process up to 5 pages for demo (remove min() for full PDF)
        pages_to_process = min(page_count, 5) 
        
        print(f"Processing {pages_to_process} pages...")
        for i in range(1, pages_to_process + 1):
            print(f"Extracting Page {i}...")
            data = extract_data_from_page(gemini_file, i)
            if data: all_data.extend(data)
            time.sleep(2) # Buffer for API limits
            
        if all_data:
            collection.delete_many({}) # Clear old data
            collection.insert_many(all_data)
            print(f"Inserted {len(all_data)} records.")
            
        genai.delete_file(gemini_file.name)
        os.remove(file_path)
        
        return {"status": "success", "records_processed": len(all_data)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_dashboard_stats():
    total = collection.count_documents({})
    if total == 0:
        return {"total": 0, "avg_cgpa": 0, "pass_fail": [], "cgpa_dist": []}

    aggr = collection.aggregate([{"$group": {"_id": None, "avg": {"$avg": "$CGPA"}}}])
    avg_cgpa = list(aggr)[0]['avg'] if total > 0 else 0

    pass_fail = list(collection.aggregate([
        {"$group": {"_id": "$Remark", "count": {"$sum": 1}}}
    ]))

    cgpas = list(collection.find({}, {"CGPA": 1, "_id": 0}))
    cgpa_values = [x['CGPA'] for x in cgpas if x.get('CGPA')]

    return {
        "total": total,
        "avg_cgpa": round(avg_cgpa, 2) if avg_cgpa else 0,
        "pass_fail": pass_fail,
        "cgpa_dist": cgpa_values
    }

class QueryRequest(BaseModel):
    query: str

@app.post("/chat")
async def chat_with_data(request: QueryRequest):
    user_q = request.query
    
    # --- UPDATED SCHEMA DEFINITION ---
    schema_info = """
    Collection Name: 'collection'
    
    Document Structure:
    {
      "Name": "AARON JESUS COSTA",  <-- NAMES ARE ALWAYS UPPERCASE
      "Seat_No": "12345",
      "CGPA": 9.5,
      "Remark": "PASSES",
      "Grand_Total": 500,
      "Subjects": [
          { "Name": "ITH-100 Computing", "Total": 75, "Grade": "A", "GP": 9 },
          { "Name": "SHM-133 Physics", "Total": 50, "Grade": "B", "GP": 7 }
      ]
    }
    """
    
    # --- UPDATED PROMPT FOR CASE INSENSITIVITY ---
    prompt = f"""
    Act as a MongoDB Query Generator. 
    User Question: "{user_q}"
    Context: {schema_info}
    
    **Query Rules:**
    1. Output ONLY executable Python/PyMongo code. No markdown.
    2. **Finding specific student:** - The DB stores names in UPPERCASE.
       - ALWAYS use Regex with option 'i' for names: `collection.find_one({{"Name": {{"$regex": "name_here", "$options": "i"}}}}, {{"_id": 0}})`
    3. **Querying Subjects:**
       - To find students who got 'A' in Physics:
         `collection.find({{"Subjects": {{"$elemMatch": {{"Name": {{"$regex": "Physics", "$options": "i"}}, "Grade": "A"}} }}}})`
       - To find marks of a student in a subject:
         Just find the student document using the Name rule above. I will parse the JSON later.
    4. **Counting:** `collection.count_documents(...)`
    5. **Aggregations (Top Scorers):**
       `collection.find().sort("Grand_Total", -1).limit(1)`
    
    Start your response with 'collection.'.
    """
    
    try:
        # 1. Generate Query
        res = llm.generate_content(prompt)
        query_str = res.text.strip().replace("```python", "").replace("```", "").strip()
        print(f"Generated Query: {query_str}")
        
        # 2. Safety Check
        valid_starts = ["collection.find", "collection.count", "collection.aggregate", "list("]
        if not any(query_str.startswith(s) for s in valid_starts):
            return {"answer": "I couldn't generate a safe query for that."}
            
        # 3. Execute
        local_scope = {"collection": collection, "list": list}
        result = eval(query_str, {}, local_scope)
        
        # Handle Cursors
        if hasattr(result, 'rewind') or hasattr(result, 'close'):
            result = list(result)
            
        # 4. Synthesize Answer
        if not result:
            return {"answer": "No matching records found in the database."}
            
        ans_prompt = f"""
        User Question: "{user_q}"
        Data Found: {str(result)}
        
        Answer the user naturally. 
        - If they asked for a specific subject mark, look inside the 'Subjects' list of the data and find it.
        - If listing students, show Name and relevant value (CGPA/Marks).
        """
        final_res = llm.generate_content(ans_prompt)
        return {"answer": final_res.text}
        
    except Exception as e:
        print(f"Error: {e}")
        return {"answer": f"Error processing that request: {e}"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)