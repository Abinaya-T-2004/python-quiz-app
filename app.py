from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = 'supersecretkey'  # secret key for session

# ---------- DATABASE SETUP ----------
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    # Create user table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )''')

    # ✅ Create score table
    c.execute('''CREATE TABLE IF NOT EXISTS scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        level TEXT NOT NULL,
        score INTEGER NOT NULL,
        total INTEGER NOT NULL
    )''')

    conn.commit()
    conn.close()

# ---------- HOME PAGE ----------
@app.route('/')
def home():
    return render_template('index.html')

# ---------- REGISTER ----------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        uname = request.form['username']
        pwd = request.form['password']

        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (uname, pwd))
            conn.commit()
            return redirect('/')
        except sqlite3.IntegrityError:
            return "Username already exists!"
        finally:
            conn.close()
    return render_template('register.html')

# ---------- LOGIN ----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        uname = request.form['username']
        pwd = request.form['password']

        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (uname, pwd))
        user = c.fetchone()
        conn.close()

        if user:
            session['username'] = uname
            return redirect('/dashboard')
        else:
            return "Invalid credentials!"
    return render_template('index.html')

# ---------- DASHBOARD ----------
@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('dashboard.html', username=session['username'])
    else:
        return redirect('/login')

# ---------- QUIZ LEVEL SELECTION ----------
@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if 'username' not in session:
        return redirect('/login')

    if request.method == 'POST':
        level = request.form['level']
        return redirect(url_for('start_quiz', level=level))
    
    return render_template('quiz.html')

# ---------- AI-BASED PYTHON QUESTIONS ----------
quiz_questions = {
    "beginner": [
        {"q": "What is the correct file extension for Python files?", "options": [".pt", ".py", ".python", ".p"], "a": ".py"},
        {"q": "What does the 'print' function do?", "options": ["Accept input", "Output text", "Define function", "None"], "a": "Output text"},
        {"q": "Which symbol is used for comments?", "options": ["//", "#", "/* */", "--"], "a": "#"},
        {"q": "What is the output of len('Python')?", "options": ["5", "6", "7", "Error"], "a": "6"},
        {"q": "What is the output of 2 + 3 * 4?", "options": ["20", "14", "10", "None"], "a": "14"},
        {"q": "Which keyword is used to define a function?", "options": ["func", "def", "define", "method"], "a": "def"},
        {"q": "Which data type is mutable?", "options": ["Tuple", "String", "List", "Int"], "a": "List"},
        {"q": "Which is a valid variable name?", "options": ["1name", "name_1", "name-1", "name.1"], "a": "name_1"},
        {"q": "What is the output of bool(0)?", "options": ["True", "False", "0", "1"], "a": "False"},
        {"q": "What does input() do?", "options": ["Prints output", "Gets user input", "Ends program", "Saves file"], "a": "Gets user input"},
        {"q": "Which one is not a keyword?", "options": ["if", "else", "loop", "while"], "a": "loop"},
        {"q": "Which operator is used for exponentiation?", "options": ["^", "**", "%", "//"], "a": "**"},
        {"q": "What is the output of type(5)?", "options": ["<class 'int'>", "int", "5", "error"], "a": "<class 'int'>"},
        {"q": "Which function returns the length of a list?", "options": ["count()", "len()", "length()", "size()"], "a": "len()"},
        {"q": "Which keyword is used to start a loop?", "options": ["loop", "iterate", "for", "next"], "a": "for"},
        {"q": "What is the output of 10 % 3?", "options": ["3", "1", "0", "10"], "a": "1"},
        {"q": "Which data type stores True/False?", "options": ["bool", "int", "str", "set"], "a": "bool"},
        {"q": "What will 'hello'.upper() return?", "options": ["HELLO", "hello", "Hello", "error"], "a": "HELLO"},
        {"q": "Which is a Python built-in data type?", "options": ["Table", "Dict", "Chart", "Graph"], "a": "Dict"},
        {"q": "What does a list start and end with?", "options": ["()", "{}", "[]", "<>"], "a": "[]"},
        {"q": "Which function adds an item to a list?", "options": ["add()", "append()", "push()", "insert()"], "a": "append()"},
        {"q": "Which one is a string?", "options": ["'Hello'", "Hello", "42", "True"], "a": "'Hello'"},
        {"q": "Which is used to import a module?", "options": ["require", "include", "import", "module"], "a": "import"},
        {"q": "What is the output of print(4 // 2)?", "options": ["2.0", "2", "2.5", "error"], "a": "2"},
        {"q": "What is the value of not True?", "options": ["False", "None", "True", "0"], "a": "False"},
        {"q": "What is the output of type('5')?", "options": ["int", "str", "float", "bool"], "a": "str"},
        {"q": "Which is not a comparison operator?", "options": ["==", "!=", "++", "<="], "a": "++"},
        {"q": "Which function converts string to int?", "options": ["str()", "int()", "float()", "input()"], "a": "int()"},
        {"q": "Which data structure does not allow duplicate values?", "options": ["List", "Tuple", "Set", "String"], "a": "Set"},
        {"q": "Which loop repeats while a condition is true?", "options": ["for", "while", "loop", "until"], "a": "while"}
    ],
    "intermediate": [
    {"q": "What is the output of: print('Hello'[::-1])?", "options": ["olleH", "Hello", "error", "None"], "a": "olleH"},
    {"q": "What is the data type of: {1, 2, 3}?", "options": ["list", "tuple", "set", "dict"], "a": "set"},
    {"q": "What does the enumerate() function return?", "options": ["index only", "values only", "index and value pairs", "None"], "a": "index and value pairs"},
    {"q": "Which method removes items from a list?", "options": ["delete()", "remove()", "pop()", "clear()"], "a": "pop()"},
    {"q": "What is a lambda function?", "options": ["named function", "loop", "anonymous function", "None"], "a": "anonymous function"},
    {"q": "Which of these is a dictionary method?", "options": ["items()", "split()", "append()", "extend()"], "a": "items()"},
    {"q": "Which module is used for regular expressions?", "options": ["os", "sys", "re", "math"], "a": "re"},
    {"q": "Which keyword is used for exception handling?", "options": ["throw", "try", "except", "catch"], "a": "except"},
    {"q": "What is the result of 10 != 5?", "options": ["True", "False", "None", "Error"], "a": "True"},
    {"q": "What is the default return type of input()?", "options": ["int", "str", "bool", "float"], "a": "str"},
    {"q": "What is the output of 3**2?", "options": ["6", "8", "9", "12"], "a": "9"},
    {"q": "Which function is used to convert a list into a set?", "options": ["list()", "set()", "tuple()", "dict()"], "a": "set()"},
    {"q": "Which loop is used to iterate over a dictionary?", "options": ["for", "while", "do-while", "each"], "a": "for"},
    {"q": "Which of these is immutable?", "options": ["list", "set", "dict", "tuple"], "a": "tuple"},
    {"q": "What does the zip() function do?", "options": ["sort", "combine iterables", "filter", "map"], "a": "combine iterables"},
    {"q": "What is the output of type([])?", "options": ["dict", "list", "set", "tuple"], "a": "list"},
    {"q": "How do you check if a value exists in a list?", "options": ["in", "has", "exists", "find"], "a": "in"},
    {"q": "What is the purpose of 'pass'?", "options": ["exit loop", "placeholder", "comment", "print"], "a": "placeholder"},
    {"q": "What is the output of list(range(3))?", "options": ["[1,2,3]", "[0,1,2]", "[0,1,2,3]", "[1,2]"], "a": "[0,1,2]"},
    {"q": "What is the result of int('10') + float('5.5')?", "options": ["15.5", "105.5", "Error", "10.5"], "a": "15.5"},
    {"q": "What does .strip() do?", "options": ["remove whitespace", "remove text", "convert to list", "capitalize"], "a": "remove whitespace"},
    {"q": "What does .split() return?", "options": ["list", "string", "set", "tuple"], "a": "list"},
    {"q": "What does the 'global' keyword do?", "options": ["create variable", "make local variable global", "delete variable", "none"], "a": "make local variable global"},
    {"q": "What is __init__ in Python?", "options": ["constructor", "loop", "module", "none"], "a": "constructor"},
    {"q": "What is the result of bool([])?", "options": ["True", "False", "None", "Error"], "a": "False"},
    {"q": "Which function returns all keys from a dict?", "options": ["dict.keys()", "dict.values()", "dict.items()", "dict.get()"], "a": "dict.keys()"},
    {"q": "How do you raise an exception?", "options": ["throw", "raise", "except", "exit"], "a": "raise"},
    {"q": "What does int('abc') return?", "options": ["0", "error", "abc", "1"], "a": "error"},
    {"q": "Which symbol is used for floor division?", "options": ["/", "//", "%", "**"], "a": "//"},
    {"q": "What is the output of list('abc')?", "options": ["['a','b','c']", "'abc'", "abc", "[abc]"], "a": "['a','b','c']"}
],

    "advanced": [
    {"q": "What is a decorator in Python?", "options": ["A loop", "A comment", "A function modifier", "An operator"], "a": "A function modifier"},
    {"q": "What does GIL stand for?", "options": ["Global Interpreter Lock", "Generic Interface Layer", "General Info Logger", "Graphical Input Language"], "a": "Global Interpreter Lock"},
    {"q": "What is the output of: print(type(lambda x: x))?", "options": ["<class 'lambda'>", "<class 'function'>", "<type>", "None"], "a": "<class 'function'>"},
    {"q": "What is a generator?", "options": ["A list", "An iterator using yield", "A decorator", "None"], "a": "An iterator using yield"},
    {"q": "Which method is called when an object is deleted?", "options": ["__del__", "__destroy__", "__remove__", "delete()"], "a": "__del__"},
    {"q": "What does @staticmethod do?", "options": ["Defines a static method", "Defines an instance method", "Defines a constructor", "None"], "a": "Defines a static method"},
    {"q": "How do you define a class in Python?", "options": ["function", "module", "class", "def class"], "a": "class"},
    {"q": "Which collection allows key-value pairs?", "options": ["List", "Set", "Tuple", "Dictionary"], "a": "Dictionary"},
    {"q": "What is monkey patching?", "options": ["Patching monkeys", "Changing behavior at runtime", "Syntax error", "None"], "a": "Changing behavior at runtime"},
    {"q": "Which protocol is used for iteration?", "options": ["__iter__ and __next__", "__getitem__ and __setitem__", "TCP/IP", "None"], "a": "__iter__ and __next__"},
    {"q": "What does *args represent?", "options": ["Keyword arguments", "Positional arguments", "All arguments", "Named tuple"], "a": "Positional arguments"},
    {"q": "What is the difference between is and ==?", "options": ["is checks identity, == checks value", "Both check value", "is checks value", "== checks identity"], "a": "is checks identity, == checks value"},
    {"q": "What is the use of __slots__?", "options": ["Add new attributes", "Restrict dynamic attribute creation", "Delete class", "None"], "a": "Restrict dynamic attribute creation"},
    {"q": "What is the output of 0.1 + 0.2 == 0.3?", "options": ["True", "False", "Error", "None"], "a": "False"},
    {"q": "What is the purpose of super()?", "options": ["Access child method", "Access parent method", "Delete object", "None"], "a": "Access parent method"},
    {"q": "How to create a virtual environment?", "options": ["venv myenv", "python -m venv myenv", "createenv", "make env"], "a": "python -m venv myenv"},
    {"q": "What is a metaclass?", "options": ["A type of class", "A decorator", "A function", "A module"], "a": "A type of class"},
    {"q": "What is the output of 'a' * 3?", "options": ["aaa", "3a", "a3", "Error"], "a": "aaa"},
    {"q": "Which of these is not thread-safe?", "options": ["list", "queue.Queue", "threading.Lock", "deque"], "a": "list"},
    {"q": "What is the default encoding in Python 3?", "options": ["ASCII", "UTF-8", "ISO", "ANSI"], "a": "UTF-8"},
    {"q": "What does 'yield' do?", "options": ["Return a value", "Stop execution", "Create a generator", "Break a loop"], "a": "Create a generator"},
    {"q": "What is __name__ used for?", "options": ["Check if file is main", "Import module", "Define method", "None"], "a": "Check if file is main"},
    {"q": "What is duck typing?", "options": ["Type checking", "Dynamic typing based on behavior", "Hardcoded typing", "None"], "a": "Dynamic typing based on behavior"},
    {"q": "What is the difference between del and remove()?", "options": ["del deletes by index, remove by value", "Both are same", "remove deletes variable", "del deletes list"], "a": "del deletes by index, remove by value"},
    {"q": "What is the output of isinstance(3, int)?", "options": ["True", "False", "int", "Error"], "a": "True"},
    {"q": "What is a context manager?", "options": ["Class with __enter__ and __exit__", "Manager class", "Module", "Loop"], "a": "Class with __enter__ and __exit__"},
    {"q": "What will open('file.txt', 'w') do?", "options": ["Read file", "Append", "Overwrite or create file", "Error"], "a": "Overwrite or create file"},
    {"q": "What does 'nonlocal' keyword do?", "options": ["Creates global var", "Changes outer function var", "Deletes var", "None"], "a": "Changes outer function var"},
    {"q": "What is the output of bool('False')?", "options": ["False", "True", "None", "Error"], "a": "True"},
    {"q": "Which module supports JSON parsing?", "options": ["csv", "json", "os", "sys"], "a": "json"}
]

}


# ---------- START QUIZ: ONE QUESTION AT A TIME ----------
@app.route('/start_quiz/<level>', methods=['GET', 'POST'])
def start_quiz(level):
    if 'username' not in session:
        return redirect('/login')

    if 'quiz_index' not in session or request.method == 'GET':
        session['quiz_index'] = 0
        session['quiz_score'] = 0
        session['quiz_level'] = level

    index = session['quiz_index']
    score = session['quiz_score']
    questions = quiz_questions.get(level)

    if request.method == 'POST':
        selected = request.form.get('answer')
        correct = questions[index]['a']
        if selected == correct:
            session['quiz_score'] = score + 1

        session['quiz_index'] = index + 1
        index = session['quiz_index']

    if index >= len(questions):
        final_score = session.pop('quiz_score', 0)
        session.pop('quiz_index', None)
        session.pop('quiz_level', None)

        # ✅ Save the score into the database
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("INSERT INTO scores (username, level, score, total) VALUES (?, ?, ?, ?)",
                  (session['username'], level, final_score, len(questions)))
        conn.commit()
        conn.close()

        return render_template('result.html', score=final_score, total=len(questions))

    # Show next question
    return render_template('question.html', question=questions[index], index=index + 1, total=len(questions))

# ---------- LOGOUT ----------
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')

# ---------- RUN APP ----------
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
