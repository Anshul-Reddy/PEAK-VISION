import mysql.connector
from flask import Flask,render_template,request,redirect

app=Flask(__name__)

connection=mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="peak_vision"
)
cursor = connection.cursor()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/notes",methods=["GET","POST"])
def notes():
    message = ""
    if request.method == "POST":
        subject = request.form["subject"]
        note=request.form["note"]
        print(subject)
        print(note)
        if subject.strip() and note.strip():
            query="""
            INSERT INTO Notes(subject,note)
            VALUES(%s,%s)
            """
            values = (subject,note)
            cursor.execute(query,values)
            connection.commit()
            
            message = "Note Saved Successfully!"
        else:
            message = "Please Fill all Fields"
    return render_template("notes.html", message = message )

@app.route("/view_notes")
def view_notes():
    cursor.execute("SELECT * FROM Notes")
    notes = cursor.fetchall()
    return render_template("view_notes.html", notes=notes)

@app.route("/delete_note/<int:id>")
def delete_note(id):
    query="DELETE FROM Notes WHERE id=%s"
    values=(id,)
    cursor.execute(query,values)
    connection.commit()
    return redirect("/view_notes")

@app.route("/edit_note/<int:id>",methods=["GET","POST"])
def edit_note(id):
    if request.method == "POST":
        subject=request.form["subject"]
        note=request.form["note"]

        query="""
        UPDATE Notes
        SET subject=%s, note=%s
        WHERE id=%s
        """
        values=(subject,note,id)
        cursor.execute(query,values)
        connection.commit()
        return redirect("/view_notes")
    query="SELECT * FROM Notes WHERE id=%s"
    values=(id,)
    cursor.execute(query,values)
    note= cursor.fetchone()
    return render_template("edit_note.html",note=note)

@app.route("/add_question",methods=["GET","POST"])
def add_question():
    message=""
    if request.method == "POST":
        subject=request.form["subject"]
        question=request.form["question"]
        difficulty=request.form["difficulty"]

        if subject.strip() and question.strip():
            query="""
            INSERT INTO questions(subjects,question,difficulty)
            VALUES(%s,%s,%s)
            """
            values=(subject,question,difficulty)
            cursor.execute(query,values)
            connection.commit()
            message="Question Added Successfully"
        else:
            message = "Please Fill All Fields"
    return render_template("add_notes.html",messahe=message)

@app.route("/question_bank")
def question_bank():
    subject = request.args.get("subject")
    if subject:
        query="""
        SELECT * FROM Questions
        WHERE subject = %s
        """
        values=(subject,)
        cursor.execute(query,values)
    else:
        cursor.execute("SELECT * FROM Questions")
    questions=cursor.fetchall()
    return render_template("question_bank.html",questions=questions)

@app.route("/complete_question/<int:id>")
def complete_question(id):
    query="""
    INSERT INTO Progress(question_id)
    VALUES(%s)
    """
    values=(id,)
    cursor.execute(query,values)
    connection.commit()
    return redirect("/question_bank")

@app.route("/progress")
def progress():
    cursor.execute("SELECT COUNT(*) FROM Questions")
    total_questions = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM Progress")
    completed_questions=cursor.fetchone()[0]

    pending_questions = total_questions-completed_questions
    if total_questions>0:
        progress_percentage=(
            completed_questions / total_questions
        ) * 100
    else:
        progress_percentage=0

    return render_template("progress.html",total_questions=total_questions,
                           completed_questions=completed_questions,pending_questions=pending_questions,
                           progress_percentage=progress_percentage)

if __name__== "__main__":
    app.run(debug=True)