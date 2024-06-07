from apps import dbconnect as db
import datetime
import pandas as pd
import calendar

def extract_previous_month() -> int:
    """
    This function extracts the previous month

    Returns:
    int : the previous month
    """
    current_month = datetime.datetime.now().month

    # create a condition if month is 1, go to december
    if current_month == 1:
        previous_month = 12
    else:
        previous_month = current_month - 1
    
    return previous_month

def extract_revenue_per_month(month_id : int = [1,2,3,4,5,6,7,8,9,10,11,12]) -> float:
    """
    This function extracts the total revenue for a given month

    Args:
    month_id : int : the month id

    Returns:
    float : the total revenue for the month
    """
    total_cost = 0
    sql = """SELECT SUM(total_cost) AS total_cost
             FROM appointments
             WHERE EXTRACT(MONTH FROM date) = %s""" 
    values = [month_id]
    cols = ['total_cost']

    try:
        total_cost = db.querydatafromdatabase(sql, values, cols)['total_cost'][0]
    except:
        pass

    return total_cost


def extract_revenue_multiple_months(month_ids = [1,2,3,4,5,6,7,8,9,10,11,12]) -> float:
    """
    This function extracts the total revenue for a given month

    Args:
    month_ids : [] : the month ids

    Returns:
    float : the total revenue for the month
    """
    total_cost = 0
    month_ids_str = str(month_ids)
    
    sql = f"""SELECT SUM(total_cost) AS total_cost
             FROM appointments
             WHERE EXTRACT(MONTH FROM date) = ANY (ARRAY{month_ids_str})""" 
    cols = ['total_cost']

    try:
        total_cost = db.querydatafromdatabase(sql, [], cols)['total_cost'][0]
    except:
        pass

    return total_cost

def average_daily_income(month_ids : list = [1,2,3,4,5,6,7,8,9,10,11,12]) -> float:
    """
    This function extracts the average daily income for a given month

    Args:
    month_id : int : the month id

    Returns:
    float : the average daily income for the month
    """
    total_cost = 0
    month_ids_str = str(month_ids)
    
    sql = f"""SELECT AVG(total_cost) AS avg_cost
             FROM appointments
             WHERE EXTRACT(MONTH FROM date) = ANY (ARRAY{month_ids_str})""" 
    cols = ['avg_cost']

    try:
        total_cost = db.querydatafromdatabase(sql, [], cols)['avg_cost'][0]
    except:
        pass

    return total_cost

def total_appointments_per_month(month_ids : list = [1,2,3,4,5,6,7,8,9,10,11,12]) -> float:
    """
    This function extracts the average appointments per day for a given month

    Args:
    month_id : int : the month id

    Returns:
    float : the average appointments per day for the month
    """
    total_appointments = 0
    month_ids_str = str(month_ids)
    
    sql = f"""SELECT COUNT(appointment_id) AS count
             FROM appointments
             WHERE EXTRACT(MONTH FROM date) = ANY (ARRAY{month_ids_str})""" 
    cols = ['count']

    try:
        total_appointments = db.querydatafromdatabase(sql, [], cols)['count'][0]
    except:
        pass

    return total_appointments

def get_months() -> list:
    """
    This function extracts the months from the database

    Returns:
    list : the months
    """
    months = []
    sql = """SELECT DISTINCT TO_CHAR(date, 'Month') AS month_name,
                CAST(TO_CHAR(date, 'MM') AS INTEGER) AS month_id
            FROM appointments"""
    
    cols = ['label', 'value']

    try:
        months = db.querydatafromdatabase(sql, [], cols)

    except:
        pass

    return months

def get_procedures() -> list:
    """
    This function extracts the procedures from the database

    Returns:
    list : the procedures
    """
    procedures = []
    sql = """SELECT DISTINCT p.procedure_name
            FROM appointment_procedure as ap
            INNER JOIN procedures as p ON ap.procedure_id =  p.procedure_id
        """
    cols = ['procedure']

    try:
        procedures = db.querydatafromdatabase(sql, [], cols)['procedure'].tolist()
    except:
        pass

    return procedures

def get_top_procedures(month_ids : list = [1,2,3,4,5,6,7,8,9,10,11,12]) -> pd.DataFrame:
    """
    This function extracts the top procedures from the database

    Returns:
    list : the top procedures
    """
    top_procedures = []
    month_ids_str = str(month_ids)

    sql = f"""SELECT p.procedure_name, COUNT(ap.procedure_id) AS count
            FROM  appointment_procedure AS ap
            INNER JOIN procedures AS p ON ap.procedure_id = p.procedure_id
            INNER JOIN appointments AS a ON a.appointment_id = ap.appointment_id
            WHERE EXTRACT(MONTH FROM a.date) = ANY (ARRAY{month_ids_str})
            GROUP BY p.procedure_name
            ORDER BY count DESC
        """
    cols = ['procedure_name', 'count']

    try:
        top_procedures = db.querydatafromdatabase(sql, [], cols)

    except Exception as e:
        
        pass
    
    return top_procedures

def generate_revenue_in_months(month_ids : list = [1,2,3,4,5,6,7,8,9,10,11,12]) -> pd.DataFrame:
    """
    This function generates revenues per month 

    Args:
    month_ids : list : the month ids

    Returns:
    pd.DataFrame : the revenues per month
    """
    month_ids_str = str(month_ids)
    sql = f"""
            SELECT EXTRACT(MONTH FROM a.date) as month, SUM(a.total_cost) as revenue
            FROM appointments as a
            WHERE EXTRACT(MONTH FROM a.date) = ANY (ARRAY{month_ids_str})
            GROUP BY month
        """

    cols = ['months', 'revenue']

    try:
        revenue = db.querydatafromdatabase(sql, [], cols)

    except Exception as e:
            
        pass
    
    return revenue
def generate_revenue_per_procedure_per_month(month_ids : list = [1,2,3,4,5,6,7,8,9,10,11,12]) -> pd.DataFrame:
    """
    This function generates the revenue per procedure for the past n number of months from the current month

    Args:
    month_ids : list : the month ids

    Returns:
    pd.DataFrame : the revenue per procedure for the past n number of months
    """
    revenue = {}
    current_month = datetime.datetime.now().month
    month_ids_str = str(month_ids)

    sql = f"""SELECT EXTRACT(MONTH FROM a.date) as month, p.procedure_name as procedure, p.procedure_cost as cost
              FROM appointment_procedure as ap
              INNER JOIN appointments as a ON ap.appointment_id = a.appointment_id
              INNER JOIN procedures as p ON ap.procedure_id = p.procedure_id
              WHERE EXTRACT(MONTH FROM a.date) = ANY (ARRAY{month_ids_str})
              GROUP BY EXTRACT(MONTH FROM a.date), p.procedure_name, p.procedure_cost
        """
    cols = ['months', 'procedure', 'revenue']

    try:
        revenue = db.querydatafromdatabase(sql, [], cols)

    except Exception as e:
        
        pass
    

    return revenue  

