"""
Cloud Notes App - GMIU Cloud Computing Assignment
A simple web application demonstrating cloud deployment,
compute services, and storage services (SQLite database).
"""

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)

# ─── Configuration ───────────────────────────────────────────────────────────
# In production (Render), DATABASE_URL env var is set automatically.
# Falls back to local SQLite for development.
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 'sqlite:///notes.db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-prod')

db = SQLAlchemy(app)

# ─── Database Model (Storage Service) ────────────────────────────────────────
class Note(db.Model):
    id        = db.Column(db.Integer, primary_key=True)
    title     = db.Column(db.String(150), nullable=False)
    content   = db.Column(db.Text, nullable=False)
    category  = db.Column(db.String(50), default='General')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Note {self.id}: {self.title}>'

# ─── Routes ───────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    """Homepage — list all notes."""
    notes = Note.query.order_by(Note.created_at.desc()).all()
    categories = db.session.query(Note.category).distinct().all()
    categories = [c[0] for c in categories]
    return render_template('index.html', notes=notes, categories=categories)


@app.route('/add', methods=['GET', 'POST'])
def add_note():
    """Add a new note."""
    if request.method == 'POST':
        title    = request.form.get('title', '').strip()
        content  = request.form.get('content', '').strip()
        category = request.form.get('category', 'General').strip()

        if not title or not content:
            flash('Title and content are required.', 'error')
            return render_template('add.html')

        note = Note(title=title, content=content, category=category)
        db.session.add(note)
        db.session.commit()
        flash('Note added successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('add.html')


@app.route('/note/<int:note_id>')
def view_note(note_id):
    """View a single note."""
    note = Note.query.get_or_404(note_id)
    return render_template('view.html', note=note)


@app.route('/delete/<int:note_id>', methods=['POST'])
def delete_note(note_id):
    """Delete a note."""
    note = Note.query.get_or_404(note_id)
    db.session.delete(note)
    db.session.commit()
    flash('Note deleted.', 'info')
    return redirect(url_for('index'))


@app.route('/health')
def health():
    """Health-check endpoint — used by the cloud platform to verify the app is alive."""
    return {'status': 'ok', 'timestamp': datetime.utcnow().isoformat()}, 200


# ─── Init DB + Run ────────────────────────────────────────────────────────────
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
