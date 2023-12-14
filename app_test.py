import unittest
from app import app, db, User, Expression
from werkzeug.security import generate_password_hash


class FlaskTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
        self.app.config["TESTING"] = True
        self.app.config["WTF_CSRF_ENABLED"] = False
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_login(self):
        with self.app.app_context():
            hashed_password = generate_password_hash("test")
            user = User(email="test@example.com", password_hash=hashed_password)
            db.session.add(user)
            db.session.commit()

        response = self.client.post(
            "/login",
            data=dict(email="test@example.com", password="test"),
            follow_redirects=True,
        )

        self.assertIn(b"Dashboard", response.data)

    def test_logout(self):
        with self.app.app_context():
            hashed_password = generate_password_hash("test")
            user = User(email="logout@example.com", password_hash=hashed_password)
            db.session.add(user)
            db.session.commit()

        self.client.post(
            "/login",
            data=dict(email="logout@example.com", password="test"),
            follow_redirects=True,
        )

        response = self.client.get("/logout", follow_redirects=True)
        self.assertIn(b"Login", response.data)

    def test_expression_evaluation(self):
        with self.app.app_context():
            hashed_password = generate_password_hash("test")
            user = User(email="test_user@example.com", password_hash=hashed_password)
            db.session.add(user)
            db.session.commit()

        self.client.post(
            "/login",
            data=dict(email="test_user@example.com", password="test"),
            follow_redirects=True,
        )

        response = self.client.post(
            "/submit_expression", data=dict(expression="2+2"), follow_redirects=True
        )

        self.assertIn(b"2+2 = 4", response.data)


def test_user_history(self):
    with self.app.app_context():
        # Create and commit the user first
        hashed_password = generate_password_hash("test")
        user = User(email="history_user@example.com", password_hash=hashed_password)
        db.session.add(user)
        db.session.commit()

        # Now add an expression linked to that user
        expression = Expression(expression="3+3", result="6", user_id=user.id)
        db.session.add(expression)
        db.session.commit()

    # Log in with the created user
    self.client.post(
        "/login",
        data=dict(email="history_user@example.com", password="test"),
        follow_redirects=True,
    )

    # Access the dashboard
    response = self.client.get("/dashboard", follow_redirects=True)
    self.assertIn(b"3+3 = 6", response.data)


if __name__ == "__main__":
    unittest.main()
