import sqlite3
import json
from datetime import datetime
from config import DATABASE_PATH


def get_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def create_database():

    conn = get_connection()
    cursor = conn.cursor()

    # ---------------- Customers ---------------- #

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Customers(

        CustomerID INTEGER PRIMARY KEY AUTOINCREMENT,

        Name TEXT NOT NULL,

        AccountNumber TEXT UNIQUE NOT NULL,

        CreatedDate TEXT NOT NULL

    )
    """)

    # ---------------- Signature Templates ---------------- #

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS SignatureTemplates(

        TemplateID INTEGER PRIMARY KEY AUTOINCREMENT,

        CustomerID INTEGER NOT NULL,

        Reference1 TEXT,

        Reference2 TEXT,

        Reference3 TEXT,

        FeatureVector TEXT,

        Statistics TEXT,

        EnrollmentDate TEXT,

        FOREIGN KEY(CustomerID)
        REFERENCES Customers(CustomerID)

    )
    """)

    # ---------------- Verification History ---------------- #

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS VerificationHistory(

        VerificationID INTEGER PRIMARY KEY AUTOINCREMENT,

        CustomerID INTEGER NOT NULL,

        Decision TEXT,

        Confidence REAL,

        VerificationTime TEXT,

        ReportPath TEXT,

        FOREIGN KEY(CustomerID)
        REFERENCES Customers(CustomerID)

    )
    """)

    conn.commit()
    conn.close()


# ==========================================================
# CUSTOMER
# ==========================================================

def add_customer(name, account_number):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO Customers
        (Name, AccountNumber, CreatedDate)

        VALUES (?, ?, ?)
    """, (

        name,

        account_number,

        datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    ))

    conn.commit()

    customer_id = cursor.lastrowid

    conn.close()

    return customer_id


def get_customer(account_number):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

        SELECT *

        FROM Customers

        WHERE AccountNumber = ?

    """, (account_number,))

    row = cursor.fetchone()

    conn.close()

    return row


def get_customer_by_id(customer_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

        SELECT *

        FROM Customers

        WHERE CustomerID = ?

    """, (customer_id,))

    row = cursor.fetchone()

    conn.close()

    return row
    

# ==========================================================
# SIGNATURE TEMPLATE
# ==========================================================

def save_template(
    customer_id,
    ref1,
    ref2,
    ref3,
    feature_vector
):

    conn = get_connection()
    cursor = conn.cursor()

    statistics = {
        "samples": 3,
        "average_duration": feature_vector.get("duration", 0.0),
        "average_velocity": feature_vector.get("mean_velocity", 0.0),
        "average_pressure": feature_vector.get("mean_pressure", 0.0),
        "average_max_pressure": feature_vector.get("max_pressure", 0.0)
    }

    cursor.execute("""
        INSERT INTO SignatureTemplates(
            CustomerID,
            Reference1,
            Reference2,
            Reference3,
            FeatureVector,
            Statistics,
            EnrollmentDate
        )
        VALUES(?,?,?,?,?,?,?)
    """, (
        customer_id,
        json.dumps(ref1),
        json.dumps(ref2),
        json.dumps(ref3),
        json.dumps(feature_vector),
        json.dumps(statistics),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()

def get_template(customer_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM SignatureTemplates
        WHERE CustomerID = ?
        ORDER BY TemplateID DESC
        LIMIT 1
    """, (customer_id,))

    row = cursor.fetchone()

    conn.close()

    if row is None:
        return None

    template = dict(row)

    # Automatically convert JSON strings to Python objects
    try:
        if template.get("Reference1"):
            template["Reference1"] = json.loads(template["Reference1"])

        if template.get("Reference2"):
            template["Reference2"] = json.loads(template["Reference2"])

        if template.get("Reference3"):
            template["Reference3"] = json.loads(template["Reference3"])

        if template.get("FeatureVector"):
            template["FeatureVector"] = json.loads(template["FeatureVector"])

        if template.get("Statistics"):
            template["Statistics"] = json.loads(template["Statistics"])

    except (json.JSONDecodeError, TypeError):
        pass
    

    return template


# ==========================================================
# HISTORY
# ==========================================================

def add_history(
    customer_id,
    decision,
    confidence,
    report_path=""
):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

        INSERT INTO VerificationHistory(

            CustomerID,

            Decision,

            Confidence,

            VerificationTime,

            ReportPath

        )

        VALUES(?,?,?,?,?)

    """, (

        customer_id,

        decision,

        confidence,

        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

        report_path

    ))

    conn.commit()

    conn.close()


def get_history():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

        SELECT

            VerificationHistory.*,

            Customers.Name,

            Customers.AccountNumber

        FROM VerificationHistory

        JOIN Customers

        ON Customers.CustomerID = VerificationHistory.CustomerID

        ORDER BY VerificationID DESC

    """)

    rows = cursor.fetchall()

    conn.close()

    return rows

def get_dashboard_statistics():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM Customers")
    customers = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM VerificationHistory
        WHERE Decision='Authentic'
    """)
    authentic = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM VerificationHistory
        WHERE Decision='Forgery'
    """)
    forgery = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM VerificationHistory
    """)
    reports = cursor.fetchone()[0]

    conn.close()

    return {

        "customers": customers,

        "authentic": authentic,

        "forgery": forgery,

        "reports": reports

    }