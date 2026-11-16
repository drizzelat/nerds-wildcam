"""Wildcam Log, sea animals (task 2 split)."""
import os
import socket
from datetime import datetime

from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.middleware.proxy_fix import ProxyFix

APP_NAME = "sea"

app = Flask(__name__)
# Behind Traefik (TLS termination + StripPrefix): trust X-Forwarded-*,
# including X-Forwarded-Prefix so url_for() builds /sea/... links.
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "sqlite:///sea.db"
)
db = SQLAlchemy(app)


class SeaSighting(db.Model):
    __tablename__ = "sea_sighting"
    id = db.Column(db.Integer, primary_key=True)
    stream = db.Column(db.String(120), nullable=False)
    animal = db.Column(db.String(120), nullable=False)
    depth_m = db.Column(db.Float, nullable=True)
    seen_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    notes = db.Column(db.Text, default="")


with app.app_context():
    db.create_all()


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        stream = request.form.get("stream", "").strip()
        animal = request.form.get("animal", "").strip()
        seen_raw = request.form.get("seen_at", "").strip()
        try:
            depth_m = float(request.form.get("depth_m", ""))
        except ValueError:
            depth_m = None
        if stream and animal:
            try:
                seen_at = datetime.fromisoformat(seen_raw)
            except ValueError:
                seen_at = datetime.now()
            db.session.add(
                SeaSighting(
                    stream=stream,
                    animal=animal,
                    depth_m=depth_m,
                    seen_at=seen_at,
                    notes=request.form.get("notes", "").strip(),
                )
            )
            db.session.commit()
        return redirect(url_for("index"))

    sightings = SeaSighting.query.order_by(SeaSighting.seen_at.desc()).all()
    return render_template(
        "index.html",
        sightings=sightings,
        now=datetime.now().strftime("%Y-%m-%dT%H:%M"),
        host=socket.gethostname(),
        peer_url=os.environ.get("PEER_URL", ""),
    )


@app.post("/delete/<int:sighting_id>")
def delete(sighting_id):
    s = db.session.get(SeaSighting, sighting_id)
    if s:
        db.session.delete(s)
        db.session.commit()
    return redirect(url_for("index"))


@app.get("/health")
def health():
    return {"status": "ok", "app": APP_NAME, "host": socket.gethostname()}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
