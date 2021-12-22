from flask import *
from flask_cors import CORS
from pages.members import members
from pages.books import books
from pages.issues import issues
from pages.returns import returns

app = Flask(__name__, template_folder="templates")
CORS(app)

app.register_blueprint(members)
app.register_blueprint(books)
app.register_blueprint(issues)
app.register_blueprint(returns)


@app.route("/")
def index():
    return "<h1>Hi</h1>"


@app.route("/photos")
def photos():
    return render_template("photos.html")


if __name__ == "__main__":
    app.run()
