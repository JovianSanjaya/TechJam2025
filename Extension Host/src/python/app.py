from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return {"message": "Hello from Flask in Docker!"}

if __name__ == "__main__":
    # Run on 0.0.0.0 so Docker can expose it outside the container
    app.run(host="0.0.0.0", port=5000, debug=True)

