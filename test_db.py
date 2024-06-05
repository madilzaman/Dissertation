from flask import Flask
import mysql.connector

app = Flask(__name__)

# MySQL configuration
mysql_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'flaskdb'
}

# Connect to the MySQL server
connection = mysql.connector.connect(**mysql_config)

# Check if the connection is successful
if connection.is_connected():
    print("Connected to MySQL database")
else:
    print("Failed to connect to MySQL database")

# Define a route for your Flask application
@app.route('/')
def index():
    # Perform database operations (e.g., execute queries)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    cursor.close()

    # Format data for display
    result = "<h1>MySQL Data</h1>"
    for row in rows:
        result += "<p>" + str(row) + "</p>"

    return result

if __name__ == '__main__':
    app.run(debug=True)
