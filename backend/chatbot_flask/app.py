from flask import Flask, request, jsonify
from flask_cors import CORS
import pyodbc
from openai import OpenAI
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
import os
from dotenv import load_dotenv
import re

app = Flask(__name__)
CORS(app)

load_dotenv(dotenv_path='./.env')
print(f"Loaded OPENAI_API_KEY: {os.getenv('OPENAI_API_KEY')}")
# Initialize OpenAI with API key from the environment variable
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

# SQL Server connection function with error handling
def connect_db():
    try:
        conn = pyodbc.connect(
            'Driver={ODBC Driver 18 for SQL Server};'
            'Server=LAPTOP-DI59H19A;'
            'Database=BayamonDb;'
            'Trusted_Connection=yes;'
            'Encrypt=no;'
            'TrustServerCertificate=yes;'
        )
        return conn
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None

# Function to get courses from the database based on a user query
def get_courses(query=None):
    conn = connect_db()
    if conn is None:
        return "Database connection error"

    try:
        cursor = conn.cursor()
        if query:
            cursor.execute("""
                SELECT * FROM tsCourse 
                WHERE CourseNo LIKE ? 
                OR CourseName LIKE ?
            """, f"%{query}%", f"%{query}%")
        else:
            cursor.execute("SELECT * FROM tsCourse")
        
        courses = cursor.fetchall()
        return courses
    except Exception as e:
        print(f"Error fetching courses: {e}")
        return []
    finally:
        conn.close()

# Function to get faculty names from the database based on the first letter
def get_faculty_names(starting_letter=None):
    conn = connect_db()
    if conn is None:
        return "Database connection error"
    
    try:
        cursor = conn.cursor()
        if starting_letter:
            cursor.execute("""
                SELECT InstructorID, FirstName, MiddleName, LastName, Gender, DepartmentID
                FROM tsInstructor
                WHERE FirstName LIKE ?
            """, f"{starting_letter}%")
        else:
            cursor.execute("""
                SELECT InstructorID, FirstName, MiddleName, LastName, Gender, DepartmentID
                FROM tsInstructor
            """)
        faculty = cursor.fetchall()
        return faculty
    except Exception as e:
        print(f"Error fetching faculty: {e}")
        return []
    finally:
        conn.close()


# Function to retrieve department name based on DepartmentID
def get_department_name(department_id):
    conn = connect_db()
    if conn is None:
        return None
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT DepartmentName FROM tsDepartment WHERE DepartmentID = ?", department_id)
        department = cursor.fetchone()
        return department[0] if department else None
    except Exception as e:
        print(f"Error fetching department name: {e}")
        return None
    finally:
        conn.close()

# Function to get faculty details by department, including gender and department information
def get_faculty_by_department(department_name=None, gender=None):
    conn = connect_db()
    if conn is None:
        return "Database connection error"

    try:
        cursor = conn.cursor()

        # Base query to join tsInstructor and tsDepartment tables
        query = """
            SELECT i.InstructorID, i.FirstName, i.MiddleName, i.LastName, i.Gender,i.DOB, d.DepartmentID, d.DepartmentName
            FROM tsInstructor i
            JOIN tsDepartment d ON i.DepartmentID = d.DepartmentID
        """

        # Handle department and gender filters
        conditions = []
        params = []
        
        if department_name:
            conditions.append("d.DepartmentName LIKE ?")
            params.append(f"%{department_name}%")
        
        if gender is not None:
            conditions.append("i.Gender = ?")
            params.append(gender)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        cursor.execute(query, params)
        faculties = cursor.fetchall()

        if not faculties:
            return []

        return faculties

    except Exception as e:
        print(f"Error fetching faculty by department: {e}")
        return []
    finally:
        conn.close()

# Function to get total number of male/female faculties, optionally filtered by department
def get_faculty_count(department_name=None, gender=None):
    conn = connect_db()
    if conn is None:
        return "Database connection error"

    try:
        cursor = conn.cursor()
        query = """
            SELECT COUNT(*), d.DepartmentName
            FROM tsInstructor i
            JOIN tsDepartment d ON i.DepartmentID = d.DepartmentID
        """

        conditions = []
        params = []
        
        if department_name:
            conditions.append("d.DepartmentName LIKE ?")
            params.append(f"%{department_name}%")
        
        if gender is not None:
            conditions.append("i.Gender = ?")
            params.append(gender)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " GROUP BY d.DepartmentName"

        cursor.execute(query, params)
        result = cursor.fetchall()

        if not result:
            return []

        # Sum total count across all departments
        total_count = sum(row[0] for row in result)

        return result, total_count

    except Exception as e:
        print(f"Error fetching faculty count: {e}")
        return []
    finally:
        conn.close()

def get_faculty_by_dob(year, condition, gender):
    conn = connect_db()
    if conn is None:
        return "Database connection error"

    try:
        cursor = conn.cursor()
        # Prepare SQL query based on the condition
        if condition == "in":
            cursor.execute("""
                SELECT i.InstructorID, i.FirstName, i.MiddleName, i.LastName, i.Gender, d.DepartmentID, d.DepartmentName, i.DOB
                FROM tsInstructor i
                JOIN tsDepartment d ON i.DepartmentID = d.DepartmentID
                WHERE YEAR(i.DOB) = ? AND (i.Gender = ? OR ? IS NULL)
            """, (year, gender, gender))
        elif condition == "before":
            cursor.execute("""
                SELECT i.InstructorID, i.FirstName, i.MiddleName, i.LastName, i.Gender, d.DepartmentID, d.DepartmentName, i.DOB
                FROM tsInstructor i
                JOIN tsDepartment d ON i.DepartmentID = d.DepartmentID
                WHERE YEAR(i.DOB) < ? AND (i.Gender = ? OR ? IS NULL)
            """, (year, gender, gender))
        elif condition == "after":
            cursor.execute("""
                SELECT i.InstructorID, i.FirstName, i.MiddleName, i.LastName, i.Gender, d.DepartmentID, d.DepartmentName, i.DOB
                FROM tsInstructor i
                JOIN tsDepartment d ON i.DepartmentID = d.DepartmentID
                WHERE YEAR(i.DOB) > ? AND (i.Gender = ? OR ? IS NULL)
            """, (year, gender, gender))
        else:
            return []

        faculties = cursor.fetchall()
        return faculties

    except Exception as e:
        print(f"Error fetching faculty by DOB: {e}")
        return []
    finally:
        conn.close()

# Function to get faculty by birth year, gender, and department
def get_faculty_by_birth_year(year, comparison, department_name=None, gender=None):
    conn = connect_db()
    if conn is None:
        return "Database connection error"

    try:
        cursor = conn.cursor()
        
        # Build the base query
        query = """
            SELECT InstructorID, FirstName, MiddleName, LastName, Gender, DOB, DepartmentID
            FROM tsInstructor
            WHERE DOB IS NOT NULL
        """
        
        # Handle gender filter
        if gender is not None:
            query += " AND Gender = ?"
        
        # Handle department filter
        if department_name:
            query += " AND DepartmentID IN (SELECT DepartmentID FROM tsDepartment WHERE DepartmentName LIKE ?)"

        # Append condition based on comparison type
        if comparison == "before":
            query += " AND DOB < ?"
        elif comparison == "after":
            query += " AND DOB > ?"
        elif comparison == "in":
            query += " AND YEAR(DOB) = ?"

        params = []
        if gender is not None:
            params.append(gender)
        if department_name:
            params.append(f"%{department_name}%")
        params.append(year)

        cursor.execute(query, params)
        faculties = cursor.fetchall()

        return faculties

    except Exception as e:
        print(f"Error fetching faculty by birth year: {e}")
        return []
    finally:
        conn.close()


# Synonym mapping for course codes
COURSE_SYNONYMS = {
    "academic management": "ACMN",
    "accounting": "ACCO",
    "adult education": "ADED",
    "air quality": "AIRQ",
    "anthropology": "ANTH",
    "aquatic studies": "AQUA",
    "architecture": "ARCH",
    "art": "ART",
    "aspiring educators": "ASPU",
    "astronomy": "ASTR",
    "atmospheric science": "ATSC",
    "banking": "BANK",
    "biological education": "BIED",
    "biology": "BIOL",
    "business project management": "BPR",
    "business introduction": "BUSI",
    "business growth": "BUSG",
    "carpentry": "CARP",
    "cisco certified network associate": "CCNA",
    "cisco certified network professional": "CCNP",
    "cisco certified network specialist": "CCNS",
    "computer engineering and electrical basics": "CEEB",
    "continuing education for university credit": "CEUC",
    "chemistry": "CHEM",
    "cooperative education application": "COAP",
    "coding": "CODE",
    "computer information systems": "COIS",
    "communication": "COM",
    "community studies": "COMM",
    "computer science": "COMP",
    "communications management": "COMU",
    "core curriculum": "CORT",
    "computer science core": "COSC",
    "computer software engineering": "COSE",
    "criminal analysis": "CRAN",
    "criminology": "CRIM",
    "criminal justice": "CRJU",
    "center for research and education": "CTRE",
    "demographics": "DEMO",
    "destination studies": "DEST",
    "digital information systems": "DIUS",
    "database management systems operations": "DMSO",
    "drafting": "DRAF",
    "diverse studies operations": "DVSO",
    "economics": "ECON",
    "environmental science": "ECS",
    "educational counseling": "EDCO",
    "educational foundations": "EDFO",
    "education research": "EDRE",
    "education specialist": "EDSP",
    "education": "EDUC",
    "educational technology": "EDUT",
    "electronics fundamentals introduction": "EFI",
    "electrical engineering": "ELEC",
    "engineering": "ENGI",
    "english literature": "ENGL",
    "environmental health": "ENHE",
    "environmental management": "ENMA",
    "engineering management": "ENMG",
    "environmental planning": "ENPL",
    "environmental science core": "ENSC",
    "environmental studies": "ENSE",
    "environmental studies techniques": "ENST",
    "ethics": "ETIC",
    "finance": "FINA",
    "french language": "FREN",
    "first-year introduction seminar": "FYIS",
    "geography": "GEOG",
    "geology": "GEOL",
    "gerontology": "GERO",
    "geospatial sciences": "GESC",
    "general studies": "GEST",
    "global education and cultural understanding": "GECU",
    "geographic information systems": "GISY",
    "graphic communication": "GRCO",
    "graphic design": "GRPH",
    "human environmental science": "HESC",
    "history": "HIST",
    "health": "HLTH",
    "humanities": "HUMA",
    "human resources": "HURE",
    "international business": "INBU",
    "instructional studies": "INST",
    "insurance": "INSU",
    "information systems and computing": "ISC",
    "italian language": "ITAL",
    "literature and arts research": "LIAR",
    "literature": "LITE",
    "mathematical computing": "MACM",
    "management": "MANA",
    "mathematical physics": "MAPH",
    "marketing": "MARK",
    "mathematics": "MAT",
    "mathematics (general)": "MATH",
    "media studies": "MEDI",
    "mechanical engineering": "MEEN",
    "merchandising": "MERE",
    "manufacturing engineering": "MFEN",
    "music": "MUSI",
    "nonprofit administration": "NADM",
    "nursing education": "NUED",
    "nursing": "NURS",
    "automotive technology": "OAUT",
    "office administration": "OFAD",
    "office information systems": "OFFI",
    "paleontology": "PALE",
    "pharmacy": "PHAR",
    "physical education": "PHED",
    "philosophy": "PHIL",
    "physical science": "PHSC",
    "pharmacy technician": "PHAT",
    "public justice studies": "PJPS",
    "project management": "PMEN",
    "practical nursing": "PNUR",
    "polymer science": "POLY",
    "political science": "POSC",
    "pruning techniques": "PRUB",
    "program management": "PRMG",
    "psychosociology": "PSCO",
    "psychology": "PSYC",
    "public administration": "PUAD",
    "quality management": "QUME",
    "quality leadership": "QYLE",
    "radiology": "RADI",
    "reading": "READ",
    "rehabilitation education": "REED",
    "restorative justice": "REST",
    "retail administration": "RETA",
    "science": "SC",
    "science education": "SCIE",
    "senior studies": "SENI",
    "social science education": "SESC",
    "site management": "SITI",
    "sociology": "SOCI",
    "social science": "SOSC",
    "social work education": "SOWE",
    "social work": "SOWO",
    "spanish": "SPAN",
    "special education": "SPED",
    "sports administration": "SPRD",
    "sports leadership": "SPLA",
    "statistics": "STAT",
    "student development": "STDE",
    "strategic management": "STRE",
    "strategic game management": "STGM",
    "survival studies": "SURV",
    "teaching assistant education": "TAE",
    "teaching assistant introduction": "TAI",
    "technical health informatics": "TEHI",
    "terrestrial studies": "TER",
    "theater arts": "THEA",
    "tomography": "TOMO",
    "transfers": "TRAN",
    "transfer accounting": "TR-ACCO",
    "transfer art": "TR-ART",
    "transfer biology": "TR-BIOL",
    "transfer business": "TR-BUSI",
    "transfer chemistry": "TR-CHEM",
    "transfer computer information systems": "TR-COIS",
    "transfer communications management": "TR-COMU",
    "transfer computer science": "TR-COSC",
    "transfer criminology": "TR-CRIM",
    "transfer criminal analysis": "TR-CRAN",
    "transfer economics": "TR-ECON",
    "transfer education": "TR-EDUC",
    "transfer electrical engineering": "TR-ELEC",
    "transfer English literature": "TR-ENGL",
    "transfer environmental management": "TR-ENMA",
    "transfer engineering management": "TR-ENMG",
    "transfer ethics": "TR-ETIC",
    "transfer environmental science": "TR-ENSC",
    "transfer finance": "TR-FINA",
    "transfer french language": "TR-FREN",
    "transfer first-year introduction seminar": "TR-FYIS",
    "transfer geography": "TR-GEOG",
    "transfer history": "TR-HIST",
    "transfer humanities": "TR-HUMA",
    "transfer human resources": "TR-HURE",
    "transfer management": "TR-MANA",
    "transfer marketing": "TR-MARK",
    "transfer mathematics": "TR-MATH",
    "transfer music": "TR-MUSI",
    "transfer nursing": "TR-NURS",
    "transfer office administration": "TR-OFAD",
    "transfer office information systems": "TR-OFFI",
    "transfer physical education": "TR-PHED",
    "transfer philosophy": "TR-PHIL",
    "transfer physical science": "TR-PHSC",
    "transfer pharmacy": "TR-PHAR",
    "transfer pharmacy technician": "TR-PHAT",
    "transfer public justice studies": "TR-PJPS",
    "transfer practical nursing": "TR-PNUR",
    "transfer political science": "TR-POSC",
    "transfer psychology": "TR-PSYC",
    "transfer quality management": "TR-QUME",
    "transfer reading": "TR-READ",
    "transfer rehabilitation education": "TR-REST",
    "transfer science education": "TR-SCIE",
    "transfer sociology": "TR-SOCI",
    "transfer social science": "TR-SOSC",
    "transfer social work": "TR-SOWO",
    "transfer spanish": "TR-SPAN",
    "transfer statistics": "TR-STAT",
    "transfer student development": "TR-STDE",
    "transfer strategic management": "TR-STRE",
    "transfer special education": "TR-SPED",
    "transfer theater arts": "TR-THEA",
    "waste management": "WAST",
    "work experience": "WORK"
}


# Function to extract course-related keywords and handle synonyms
def extract_course_keywords(user_query):
    """
    Extract relevant keywords from user input for course lookup. Handles both course codes
    and general terms by mapping them to specific course numbers or abbreviations.
    """
    # Capture common course code patterns like "SOSC", "ACCO", or "102"
    pattern = re.compile(r'\b[A-Z]{4}\b|\b\d{3,4}\b')
    keywords = pattern.findall(user_query)
    
    if not keywords:
        # Find synonyms in the user query
        for term, code in COURSE_SYNONYMS.items():
            if term in user_query.lower():
                return code
    
    return " ".join(keywords) if keywords else user_query

# Function to extract faculty-related keywords and handle the first letter condition
def extract_faculty_keywords(user_query):
    """
    Extract relevant keywords for faculty lookup based on the starting letter.
    """
    pattern = re.compile(r'\b(?:whose name starts with|faculty starting with|name starting with|names starting with)\s([A-Za-z])', re.IGNORECASE)
    match = pattern.search(user_query)
    
    return match.group(1).upper() if match else None

# Function to handle fallback responses
def fallback_response(user_query):
    """
    Generates a polite fallback response if no courses are found.
    """
    return f"""
    I'm sorry, but we couldn't find any courses related to "{user_query}" in our database. 
    You might want to try searching with different keywords or reach out to your academic advisor for more information.
    """

# Function to detect common greetings or casual conversationd 
def is_greeting(user_query):
    """
    Detects if the user query is a greeting or casual conversation like 'Hi', 'Hello', etc.
    """
    greetings = ["hi", "hello", "hey", "greetings", "what's up", "good morning", "good afternoon", "good evening"]
    return any(greeting in user_query.lower() for greeting in greetings)


# Define DatabaseProxyAgent for handling queries and fetching results from the database
class DatabaseProxyAgent(RetrieveUserProxyAgent):
    def __init__(self, name):
        super().__init__(name=name, retrieve_config={"docs_path": None})

    def message_generator(self, assistant, user_query):
        """
        Handles different types of user queries (courses or faculty).
        """
        if is_greeting(user_query):
            return {"response": "Hello! How can I assist you today?", "course_list": [], "faculty_list": []}

        # Handling queries about faculty birth year
        birth_year_pattern = re.compile(r"(?P<comparison>before|after|in) (?P<year>\d{4})")
        match = birth_year_pattern.search(user_query.lower())
        if match:
            comparison = match.group('comparison')
            year = int(match.group('year'))

            gender = None
            if "male" in user_query.lower():
                gender = 1
            elif "female" in user_query.lower():
                gender = 0

            department_name = None
            department_pattern = re.compile(r'in (.+) department', re.IGNORECASE)
            dept_match = department_pattern.search(user_query)
            if dept_match:
                department_name = dept_match.group(1).strip()

            faculties = get_faculty_by_birth_year(year, comparison, department_name, gender)
            if not faculties:
                return {"response": f"No faculty found for the given criteria.", "faculty_list": []}

            faculty_list = [
                {
                    "id": fac[0],
                    "name": " ".join([part for part in [fac[1], fac[2], fac[3]] if part]),
                    "gender": "Male" if fac[4] == 1 else "Female",
                    "dob": fac[5].strftime("%Y-%m-%d"),  # Format the DOB
                    "department": get_department_name(fac[6])  # Get the department name
                }
                for fac in faculties
            ]

            faculty_list_str = "\n".join(
                [f"Faculty Name: {fac['name']}, Gender: {fac['gender']}, DOB: {fac['dob']}, Department: {fac['department']}"
                for fac in faculty_list]
            )

            return {
                "response": f"Here are the names and date of birth of {'male' if gender == 1 else 'female'} faculties who are born {comparison} the year {year}:\n{faculty_list_str}",
                "faculty_list": faculty_list
            }


        # Handling faculty queries
        if "faculty" in user_query.lower() or "faculties" in user_query.lower():
            starting_letter = extract_faculty_keywords(user_query)
            
            if starting_letter:
                # Fetch faculty whose names start with the specified letter
                faculties = get_faculty_names(starting_letter)
                if not faculties:
                    return {"response": f"No faculty found whose name starts with {starting_letter}.", "faculty_list": []}

                # Prepare the response for listing faculties
                faculty_list = [
                    {
                        "id": fac[0],
                        "name": " ".join([part for part in [fac[1], fac[2], fac[3]] if part]),
                        "gender": "Male" if fac[4] == 1 else "Female",
                        "department": fac[5]
                    }
                    for fac in faculties
                ]

                faculty_list_str = "\n".join(
                    [f"Faculty Name: {fac['name']}, Gender: {fac['gender']}, Department: {fac['department']}"
                    for fac in faculty_list]
                )

                return {
                    "response": f"List of faculty whose name starts with {starting_letter}:\n{faculty_list_str}",
                    "faculty_list": faculty_list
                }

        # Handling faculty by department and gender queries
        if "faculty" in user_query.lower() or "faculties" in user_query.lower() or "male" in user_query.lower() or "female" in user_query.lower():
            department_name = None
            gender = None

            # Extract department name and gender from the query
            if "female" in user_query.lower():
                gender = 0
            elif "male" in user_query.lower():
                gender = 1

            faculties = get_faculty_by_department(department_name, gender)
            # Extract department name
            department_pattern = re.compile(r'in (.+) department', re.IGNORECASE)
            match = department_pattern.search(user_query)
            if match:
                department_name = match.group(1).strip()

            # Handle faculty listing based on department and gender
            if "list" in user_query.lower() or "show" in user_query.lower():
                faculties = get_faculty_by_department(department_name, gender)
                if not faculties:
                    return {"response": f"No faculty found for the given criteria.", "faculty_list": []}

                faculty_list = [
                    {
                        "id": fac[0],
                        "name": " ".join([part for part in [fac[1], fac[2], fac[3]] if part]),
                        "gender": "Male" if fac[4] == 1 else "Female",
                        "department": fac[6]
                    }
                    for fac in faculties
                ]

                faculty_list_str = "\n".join(
                    [f"Faculty Name: {fac['name']}, Gender: {fac['gender']}, Department: {fac['department']}"
                    for fac in faculty_list]
                )

                return {
                    "response": f"List of faculty in {department_name or 'all departments'}:\n{faculty_list_str}",
                    "faculty_list": faculty_list
                }
            
            # Handle count queries
            elif "number" in user_query.lower() or "count" in user_query.lower():
                faculty_count, total_count = get_faculty_count(department_name, gender)
                if not faculty_count:
                    return {"response": f"No faculty count available for the given criteria.", "faculty_list": []}

                count_str = "\n".join(
                    [f"{row[0]} faculty members in {row[1]} department" for row in faculty_count]
                )

                return {
                    "response": f"Faculty count by department:\n{count_str}\n\nTotal faculty: {total_count}",
                    "faculty_list": []
                }
        
        # Handle course queries as before
        else:
            keywords = extract_course_keywords(user_query)
            courses = get_courses(keywords)

            if not courses:
                return {"response": fallback_response(user_query), "course_list": []}

            course_list = [
                {"id": course[0], "course_no": course[1], "name": course[2]}
                for course in courses
            ]

            course_list_str = "\n".join(
                [f"Course ID: {course['id']}, Course No: {course['course_no']}, Course Name: {course['name']}"
                for course in course_list]
            )

            prompt = f"""
            User Query: {user_query}
            
            Retrieved Courses:
            {course_list_str}
            
            Based on the user's query and the retrieved course information, provide a helpful response.
            """

            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}]
                )
                final_response = response.choices[0].message.content.strip()

                return {"response": final_response, "course_list": course_list}

            except Exception as e:
                print(f"Error generating response: {e}")
                return {"response": f"Error generating response: {e}", "course_list": []}
        
# Initialize the DatabaseProxyAgent
ragproxyagent = DatabaseProxyAgent(name="ragproxyagent")

# Flask route to handle chat requests
@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_message = request.json.get('message')
        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        # Generate response using the DatabaseProxyAgent
        result = ragproxyagent.message_generator(None, user_message)

        # Return the assistant's response 
        return jsonify({"message": result["response"], "courses": result.get("course_list", []), "faculty": result.get("faculty_list", [])})

    except Exception as e:
        print(f"Error in /chat route: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)