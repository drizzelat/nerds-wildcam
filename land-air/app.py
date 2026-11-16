"""Wildcam Log, land & air animals (task 2 split)."""
import os
import socket
from datetime import datetime

from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.middleware.proxy_fix import ProxyFix

APP_NAME = "land-air"
KINDS = ("land", "air")

app = Flask(__name__)
# Behind Traefik (TLS termination + StripPrefix): trust X-Forwarded-*,
# including X-Forwarded-Prefix so url_for() builds /land/... links.
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "sqlite:///land-air.db"
)
db = SQLAlchemy(app)


class LandAirSighting(db.Model):
    __tablename__ = "land_air_sighting"
    id = db.Column(db.Integer, primary_key=True)
    stream = db.Column(db.String(120), nullable=False)
    animal = db.Column(db.String(120), nullable=False)
    kind = db.Column(db.String(10), nullable=False, default="land")
    seen_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    notes = db.Column(db.Text, default="")


with app.app_context():
    db.create_all()


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        stream = request.form.get("stream", "").strip()
        animal = request.form.get("animal", "").strip()
        kind = request.form.get("kind", "land")
        seen_raw = request.form.get("seen_at", "").strip()
        if stream and animal:
            try:
                seen_at = datetime.fromisoformat(seen_raw)
            except ValueError:
                seen_at = datetime.now()
            db.session.add(
                LandAirSighting(
                    stream=stream,
                    animal=animal,
                    kind=kind if kind in KINDS else "land",
                    seen_at=seen_at,
                    notes=request.form.get("notes", "").strip(),
                )
            )
            db.session.commit()
        return redirect(url_for("index"))

    sightings = LandAirSighting.query.order_by(LandAirSighting.seen_at.desc()).all()
    return render_template(
        "index.html",
        sightings=sightings,
        kinds=KINDS,
        now=datetime.now().strftime("%Y-%m-%dT%H:%M"),
        host=socket.gethostname(),
        peer_url=os.environ.get("PEER_URL", ""),
    )


@app.post("/delete/<int:sighting_id>")
def delete(sighting_id):
    s = db.session.get(LandAirSighting, sighting_id)
    if s:
        db.session.delete(s)
        db.session.commit()
    return redirect(url_for("index"))


@app.get("/health")
def health():
    return {"status": "ok", "app": APP_NAME, "host": socket.gethostname()}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
