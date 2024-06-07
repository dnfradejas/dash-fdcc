import psycopg2
import pandas as pd
import os
from dotenv import load_dotenv

# load environment variables
load_dotenv()

def getdblocation():
    # define connection string
    db = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        port = os.getenv('DB_PORT')
    )

    return db

def getdblocation():
    # define connection string
    db = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )

    return db

# print(getdblocation())
def modifydatabase(sql, values):
    db = getdblocation()

    # we create a cursor object
    cursor = db.cursor()

    # we execute the query
    cursor.execute(sql, values)

    # we commit the changes
    db.commit()

    # we close the cursor
    cursor.close()

def querydatafromdatabase(sql, values, dfcolumns):
    db = getdblocation()

    # we create a cursor object
    cursor = db.cursor()

    # we execute the query
    cursor.execute(sql, values)

    # we fetch all the results

    # we create a dataframe
    df = pd.DataFrame(cursor.fetchall(), columns=dfcolumns)
    
    # we close the cursor
    cursor.close()

    return df

def modifydatabasewithreturning(sql, values):
    db = getdblocation()

    # we create a cursor object
    cursor = db.cursor()

    # we execute the query
    cursor.execute(sql, values)

    # we fetch all the results
    result = cursor.fetchone()

    # we commit the changes
    db.commit()

    # we close the cursor
    cursor.close()

    return result



# print(extract_revenue_multiple_months([3,5]))
# sql = """ SELECT firstname, lastname FROM patients """
# values = []
# cols = ['firstname', 'lastname']

# print(querydatafromdatabase(sql, values, cols)['firstname'].tolist())