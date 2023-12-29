from flask import Flask,render_template,request,redirect,url_for,session
import mysql.connector
import datetime

connection =mysql.connector.connect(host='localhost',user='root',password='Password',database='taskmanagementsystem')
mycursor=connection.cursor()

app=Flask(__name__)
app.secret_key = 'Geethu123'

@app.route('/')
def Home():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/AddTasks')
def AddTasks():
    return render_template('AddTask.html')

@app.route('/main')
def main():
    username=session['username']
    task_count= Completed_Task()
    Inprogress=Inprogress_Task()
    Pending=Pending_Task()
    return render_template('main.html',task_count=task_count,Inprogress=Inprogress,Pending=Pending,username=username)

@app.route('/logout')
def logout():
    session.clear()
    return render_template('login.html')

def is_user_exists(username, email):
    try:
        query = "SELECT * FROM employees WHERE username = %s OR email = %s"
        data = (username, email)
        mycursor.execute(query, data)
        result = mycursor.fetchone()

        return result is not None 
    except Exception as e:
        return False

@app.route('/addemployee',methods=['GET', 'POST'])
def AddEmployee():
    name=request.form.get('empname')
    username=request.form.get('empusername')
    email=request.form.get('email')
    phone=request.form.get('phone')
    password=request.form.get('password')
    cpassword=request.form.get('cpassword')

    if password==cpassword:


        if is_user_exists(username, email):
            msg = 'User already exists!'
            return render_template('/login.html', msg=msg)

        query="INSERT INTO employees (emp_name,email,phone,username,password) VALUES (%s,%s,%s,%s,%s)"
        data=(name,email,phone,username,password)
    else:
        error_msg = 'Passwords do not match. Please try again.'
        return render_template('/register.html',error_msg=error_msg)
    mycursor.execute(query,data)
    connection.commit()
    msg = 'You have successfully registered !'
    return render_template('/login.html',msg=msg)

@app.route('/empHome',methods=['GET', 'POST'])
def Login():
    if request.method=='POST':
        username=request.form.get('username')
        password=request.form.get('password')
        query = "SELECT * FROM employees WHERE username=%s and password=%s"
        values=(username,password)
        mycursor.execute(query,values)
        data = mycursor.fetchone()
        if data:
            session['loggedin'] = True
            session['id'] = data[0]
            session['username'] = data[4]
            msg= 'Logged in successfully!'
            username=session['username']
            task_count= Completed_Task()
            Inprogress=Inprogress_Task()
            Pending=Pending_Task()
            return render_template('main.html', msg = msg , task_count=task_count,Inprogress=Inprogress,Pending=Pending,username=username)
        else:
            msg = 'Incorrect username/password!'
    return render_template('login.html', msg=msg)
    
@app.route('/ViewTask')
def ViewTask():
    user_id = session['id']
    query = "SELECT * FROM Tasks where emp_id=%s order by Task_id desc"
    value=(user_id,)
    mycursor.execute(query,value)
    data = mycursor.fetchall()
    username=session['username']
    return render_template('ViewTask.html',sqldata=data,username=username)

def get_current_datetime():
    return datetime.datetime.now().strftime('%Y-%m-%d')

def get_task_data_by_id(task_id):
    try:
        query = "SELECT * FROM Tasks WHERE Task_id =%s"
        data = (task_id,)
        mycursor.execute(query, data)
        task_data = mycursor.fetchone()

        if task_data:
            task_dict = {
                'Task_id':task_data[0],
                'Title': task_data[1],
                'Descriptions': task_data[2],
                'Due_date': task_data[3],
                'Statuss': task_data[4],
                'Created_date': task_data[5],
                'Category': task_data[6]
            }
            return task_dict
        else:
            return None
    except Exception as e:
        print(f"Error in get_task_data_by_id: {e}")
        return None

@app.route('/AddTask', methods=['GET', 'POST'])
def AddTask():
    username=session['username']
    print(username)
    form_data = None 
    msg = '' 
    current_datetime = get_current_datetime()
    action = 'create'
    task_id = request.args.get('id')
    if task_id:
        form_data = get_task_data_by_id(task_id)
        action = 'update'
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'create':
            user_id = session['id']
            title = request.form.get('title')
            description = request.form.get('description')
            due_date = request.form.get('dueDate')
            status = request.form.get('status')
            category = request.form.get('category')
            current_datetime = get_current_datetime()
            
            query = "INSERT INTO Tasks ( Title, Descriptions, Due_date, Statuss, Created_date, Category, emp_id) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            data = (title, description, due_date, status, current_datetime, category, user_id)

            mycursor.execute(query, data)
            connection.commit()

            msg = 'Task Created successfully!'
            return redirect(url_for('ViewTask'))
        elif action == 'update':
            user_id = session['id']
            title = request.form.get('title')
            description = request.form.get('description')
            due_date = request.form.get('dueDate')
            status = request.form.get('status')
            category = request.form.get('category')
            task_id=request.form.get('id')

            query = "UPDATE Tasks SET Title=%s, Descriptions=%s, Due_date=%s, Statuss=%s, Category=%s WHERE emp_id=%s AND Task_id=%s"
            data = (title, description, due_date, status, category, user_id, task_id)

            mycursor.execute(query, data)
            connection.commit()

            msg = 'Task Updated successfully!'
            return redirect(url_for('ViewTask'))
    
    return render_template('AddTask.html', form_data=form_data, msg=msg,current_datetime=current_datetime,action=action,username=username)

@app.route('/DeleteTask/<int:task_id>', methods=['GET', 'POST'])
def DeleteTask(task_id):
    try:
        user_id = session['id']
        query = "DELETE FROM Tasks WHERE emp_id=%s AND Task_id=%s"
        data = (user_id, task_id)
        mycursor.execute(query, data)
        connection.commit()
        msg = 'Task Deleted successfully!'
    except Exception as e:
        print(f"Error in DeleteTask: {e}")
        msg = 'Error deleting task.'

    return redirect(url_for('ViewTask'))

def Completed_Task():
    if 'loggedin' in session:
        user_id = session['id']
        query = "SELECT count(emp_id) FROM Tasks where emp_id=%s and Statuss='Completed'"
        value=(user_id,)
        mycursor.execute(query,value)
        completed_task_count = mycursor.fetchone()[0]
        return completed_task_count

def Inprogress_Task():
    if 'loggedin' in session:
        user_id = session['id']
        query = "SELECT count(emp_id) FROM Tasks where emp_id=%s and Statuss='InProgress'"
        value=(user_id,)
        mycursor.execute(query,value)
        Inprogress_count = mycursor.fetchone()[0]
        return Inprogress_count

def Pending_Task():
    if 'loggedin' in session:
        user_id = session['id']
        query = "SELECT count(emp_id) FROM Tasks where emp_id=%s and Statuss='pending'"
        value=(user_id,)
        mycursor.execute(query,value)
        Pending_count = mycursor.fetchone()[0]
        return Pending_count
    
@app.route('/FilterTask', methods=['GET', 'POST'])
def FilterTask():
        if 'loggedin' in session:
            username=session['username']
            user_id = session['id']
            category_filter = request.args.get('categoryFilter', '')
            status_filter = request.args.get('statusFilter', '')

            query = """
            SELECT * FROM Tasks
            WHERE emp_id = %s
              AND (COALESCE(%s, '') = '' OR Category = %s)
              AND (COALESCE(%s, '') = '' OR Statuss = %s)
            """
            values = (user_id, category_filter, category_filter, status_filter, status_filter)
            mycursor.execute(query, values)
            filtered_data = mycursor.fetchall()
        return render_template('ViewTask.html',sqldata=filtered_data,username=username)




if __name__=='__main__':
    app.run(debug=True)