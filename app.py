from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user,
)


class Parser:
    def __init__(self, expression):
        self.expression = expression
        self.index = 0
        self.current_char = expression[self.index]

    def advance(self):
        self.index += 1
        if self.index < len(self.expression):
            self.current_char = self.expression[self.index]
        else:
            self.current_char = None

    def parse(self):
        return self.expr()

    def eat(self, char_type):
        if self.current_char == char_type:
            self.advance()
        else:
            raise ValueError(f"Expected character {char_type}")

    def factor(self):
        if self.current_char.isdigit():
            num = ""
            while self.current_char is not None and self.current_char.isdigit():
                num += self.current_char
                self.advance()
            return int(num)
        elif self.current_char == "(":
            self.eat("(")
            result = self.expr()
            self.eat(")")
            return result
        else:
            raise ValueError("Invalid character")

    def term(self):
        result = self.factor()
        while self.current_char in ["*", "/"]:
            if self.current_char == "*":
                self.eat("*")
                result *= self.factor()
            elif self.current_char == "/":
                self.eat("/")
                divisor = self.factor()
                if divisor == 0:
                    raise ValueError("Division by zero")
                result /= divisor
        return result

    def expr(self):
        result = self.term()
        while self.current_char in ["+", "-"]:
            if self.current_char == "+":
                self.eat("+")
                result += self.term()
            elif self.current_char == "-":
                self.eat("-")
                result -= self.term()
        return result


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SECRET_KEY"] = "your_secret_key"

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password_hash = db.Column(db.String(100))
    expressions = db.relationship("Expression", backref="author", lazy=True)


class Expression(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    expression = db.Column(db.String(100), nullable=False)
    result = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/")
def index():
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")

        new_user = User(email=email, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for("dashboard"))

        flash("Invalid email or password")
    return render_template("login.html")


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", expressions=current_user.expressions)


@app.route("/submit_expression", methods=["POST"])
@login_required
def submit_expression():
    if request.method == "POST":
        expression_text = request.form["expression"]

        try:
            parser = Parser(expression_text)
            result = parser.parse()
        except ValueError as e:
            flash(str(e))
            return redirect(url_for("dashboard"))

        new_expression = Expression(
            expression=expression_text, result=str(result), user_id=current_user.id
        )
        db.session.add(new_expression)
        db.session.commit()

        return redirect(url_for("dashboard"))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
