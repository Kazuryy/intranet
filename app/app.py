from flask import Flask
from routes.devoirs import devoirs_bp

app = Flask(__name__)
app.register_blueprint(devoirs_bp)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)