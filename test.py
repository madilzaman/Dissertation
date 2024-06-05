import mysql.connector

# Connect to the MySQL server
connection = mysql.connector.connect(
    host='localhost',
    user='root',
    password='',
    database='flaskdb'
)

# Check if the connection is successful
if connection.is_connected():
    print("Connected to MySQL database")

    # Perform database operations (e.g., execute queries)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()

    for row in rows:
        print(row)

    # Close cursor and connection
    cursor.close()
    connection.close()
    print("MySQL connection is closed")
else:
    print("Failed to connect to MySQL database")
