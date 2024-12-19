from flask import Flask, render_template, request, redirect, url_for, flash, session,jsonify
from flask_mysqldb import MySQL
from functools import wraps
import MySQLdb.cursors
import re
import hashlib

app = Flask(__name__)

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '1234'
app.config['MYSQL_DB'] = 'e_governance'
app.config['SECRET_KEY'] = 'your-secret-key'

mysql = MySQL(app)

# Login decorator for securing routes
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Employee login decorator
def employee_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_type' not in session or session['user_type'] != 'employee':
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_type = request.form['user_type']
        username = request.form['username']
        password = request.form['password']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        if user_type == 'employee':
            cursor.execute('SELECT * FROM Login WHERE Usname = %s AND pwd = %s', (username, password,))
            account = cursor.fetchone()
            if account:
                session['logged_in'] = True
                session['user_type'] = 'employee'
                session['username'] = username
                session['emp_id'] = account['emp_id']
                return redirect(url_for('employee_dashboard'))
        else:
            cursor.execute('SELECT * FROM Citizen_Login WHERE Usname = %s AND pwd = %s', (username, password,))
            account = cursor.fetchone()
            if account:
                session['logged_in'] = True
                session['user_type'] = 'citizen'
                session['username'] = username
                session['aadhar'] = account['Aadhar']
                return redirect(url_for('citizen_dashboard'))
                
        flash('Invalid username/password!')
    return render_template('login.html')

@app.route('/employee/dashboard')
@login_required
@employee_required
def employee_dashboard():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # Get employee permissions
    cursor.execute('''
        SELECT p.type 
        FROM Permission p 
        JOIN Employees e ON p.emp_id = e.emp_id 
        WHERE e.emp_id = %s
    ''', (session['emp_id'],))
    
    permissions = cursor.fetchall()
    return render_template('employee_dashboard.html', permissions=permissions)

@app.route('/citizen/dashboard')
@login_required
def citizen_dashboard():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # Get available services
    cursor.execute('SELECT * FROM Services')
    services = cursor.fetchall()
    
    # Get vacancies
    cursor.execute('''
        SELECT c.name, v.locality, v.vacancies, v.salary 
        FROM Vacancies v 
        JOIN Companies c ON v.Company_id = c.Company_id
    ''')
    vacancies = cursor.fetchall()
    
    # Get PDS details (if needed)
    cursor.execute('SELECT * FROM PDS WHERE Aadhar = %s', (session['aadhar'],))
    pds_details = cursor.fetchall()
    
    return render_template('citizen_dashboard.html', 
                           services=services,
                           vacancies=vacancies,
                           pds_details=pds_details,
                           view="dashboard")

@app.route('/view_csc_centers')
@login_required
def view_csc_centers():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # Get CSC center details along with the services they provide
    cursor.execute('''
        SELECT c.csc_id, c.centre_name, c.location, c.Phone_no, s.serv
        FROM csc c
        JOIN service_csc sc ON c.csc_id = sc.csc_id
        JOIN services s ON sc.serv_code = s.serv_code
    ''')
    
    csc_services = cursor.fetchall()

    # Organize the data to group services by each CSC center
    csc_centers = {}
    for row in csc_services:
        csc_id = row['csc_id']
        if csc_id not in csc_centers:
            csc_centers[csc_id] = {
                'centre_name': row['centre_name'],
                'location': row['location'],
                'Phone_no': row['Phone_no'],
                'services': []
            }
        csc_centers[csc_id]['services'].append(row['serv'])
    
    # Convert dictionary to list for easier handling in template
    csc_centers_list = list(csc_centers.values())

    return render_template('citizen_dashboard.html', 
                           csc_centers=csc_centers_list,
                           view="csc_centers")


def get_primary_key_column(table_name):
    """
    Retrieves the primary key column name for the given table.
    """
    cursor = mysql.connection.cursor()
    cursor.execute(f"SHOW KEYS FROM {table_name} WHERE Key_name = 'PRIMARY'")
    result = cursor.fetchone()
    cursor.close()
    return result[4] if result else None  # Column name is in the fifth field (index 4)

@app.route('/employee/manage/<table_name>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@login_required
@employee_required
def manage_table(table_name):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # Get the primary key column dynamically
    primary_key_column = get_primary_key_column(table_name)
    if not primary_key_column:
        flash(f"Primary key not found for table {table_name}.")
        return redirect(url_for('employee_dashboard'))
    
    # Fetch all records for display
    if request.method == 'GET':
        cursor.execute(f'SELECT * FROM {table_name}')
        data = cursor.fetchall()
        return render_template('manage_table.html', table_name=table_name, data=data, primary_key_column=primary_key_column)
    
    # Handle INSERT operation
    elif request.method == 'POST':
        columns = ', '.join(request.form.keys())
        values = tuple(request.form.values())
        placeholders = ', '.join(['%s'] * len(values))
        
        cursor.execute(f'INSERT INTO {table_name} ({columns}) VALUES ({placeholders})', values)
        mysql.connection.commit()
        flash(f'Record added successfully to {table_name}')
        return redirect(url_for('manage_table', table_name=table_name))
    
    # Handle DELETE operation
    elif request.method == 'DELETE':
        record_key = request.args.get(primary_key_column)
        cursor.execute(f'DELETE FROM {table_name} WHERE {primary_key_column} = %s', (record_key,))
        mysql.connection.commit()
        return jsonify(success=True)
    
    # Handle UPDATE operation
    elif request.method == 'PUT':
        record_key = request.args.get(primary_key_column)
        updates = ', '.join([f"{k} = %s" for k in request.form.keys()])
        values = list(request.form.values()) + [record_key]
        
        cursor.execute(f'UPDATE {table_name} SET {updates} WHERE {primary_key_column} = %s', values)
        mysql.connection.commit()
        flash(f'Record updated successfully in {table_name}')
        return jsonify(success=True)

    cursor.close()

# Citizen specific routes
@app.route('/citizen/services')
@login_required
def view_services():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM Services')
    services = cursor.fetchall()
    return render_template('services.html', services=services)

@app.route('/citizen/vacancies')
@login_required
def view_vacancies():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('''
        SELECT c.name, v.locality, v.vacancies, v.salary 
        FROM Vacancies v 
        JOIN Companies c ON v.Company_id = c.Company_id
    ''')
    vacancies = cursor.fetchall()
    return render_template('vacancies.html', vacancies=vacancies)

@app.route('/citizen/csc')
@login_required
def view_csc():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('''
        SELECT c.*, d.Dept_name 
        FROM CSC c 
        JOIN Department d ON c.Dept_id = d.Dept_id
    ''')
    csc_centers = cursor.fetchall()
    return render_template('csc.html', csc_centers=csc_centers)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user_type', None)
    session.pop('username', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
