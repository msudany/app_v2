from flask import Flask
from extensions import db, login_manager

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///book_app.db'
app.config['SECRET_KEY'] = 'your_secret_key'

# Initialize extensions
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

# Import models, routes, and other modules
from models import *
from routes import *
from auth import *

# Create tables and seed data
@app.before_request
def initialize_database():
    db.create_all()
    from seed import seed_data
    seed_data()

# Error Handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)
