# app.py
# Project: contact_management_system
# Author: Rohit
# Date: 2026-04-29
# Description: Simple contact management system (Flask). Single-file app with CRUD, search, and file persistence.

from flask import Flask, render_template_string, request, redirect, url_for, flash
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "change_this_for_production"

DATA_FILE = "contacts.json"

def load_contacts():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_contacts(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

contacts = load_contacts()

def next_id():
    return max((c.get("id", 0) for c in contacts), default=0) + 1

@app.route("/_health")
def health():
    return "OK", 200

# --- Full-page templates (no inheritance) ---
INDEX_HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Contact Management System</title>
  <link rel="stylesheet" href="{{ url_for('styles') }}">
</head>
<body>
  <header class="site-header">
    <div class="container">
      <h1><a href="{{ url_for('index') }}">Contact Management System</a></h1>
      <nav>
        <a href="{{ url_for('index') }}">Home</a>
        <a href="{{ url_for('add_contact') }}">Add Contact</a>
      </nav>
    </div>
  </header>

  <main class="container">
    {% with messages = get_flashed_messages(with_categories=true) %}
      {% if messages %}
        <div class="flash-list">
          {% for category, msg in messages %}
            <div class="flash {{ category }}">{{ msg }}</div>
          {% endfor %}
        </div>
      {% endif %}
    {% endwith %}

    <section class="toolbar">
      <form method="get" action="{{ url_for('index') }}" class="search-form">
        <input type="text" name="q" placeholder="Search by name or phone" value="{{ q|default('') }}">
        <button type="submit">Search</button>
        {% if q %}
          <a class="clear" href="{{ url_for('index') }}">Clear</a>
        {% endif %}
      </form>
    </section>

    <section class="list">
      {% if contacts %}
        <table class="contacts-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Phone</th>
              <th>Email</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {% for c in contacts %}
              <tr>
                <td>{{ c.name }}</td>
                <td>{{ c.phone }}</td>
                <td>{{ c.email }}</td>
                <td class="actions">
                  <a href="{{ url_for('edit_contact', contact_id=c.id) }}">Edit</a>
                  <form method="post" action="{{ url_for('delete_contact', contact_id=c.id) }}" onsubmit="return confirm('Delete this contact?');" style="display:inline">
                    <button type="submit" class="link-button">Delete</button>
                  </form>
                </td>
              </tr>
            {% endfor %}
          </tbody>
        </table>
      {% else %}
        <p>No contacts yet. <a href="{{ url_for('add_contact') }}">Add a contact</a>.</p>
      {% endif %}
    </section>
  </main>

  <footer class="site-footer">
    <div class="container">
      <p>© {{ year }} Contact Management System</p>
    </div>
  </footer>
</body>
</html>
"""

ADD_HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Add Contact - Contact Management System</title>
  <link rel="stylesheet" href="{{ url_for('styles') }}">
</head>
<body>
  <header class="site-header">
    <div class="container">
      <h1><a href="{{ url_for('index') }}">Contact Management System</a></h1>
      <nav>
        <a href="{{ url_for('index') }}">Home</a>
        <a href="{{ url_for('add_contact') }}">Add Contact</a>
      </nav>
    </div>
  </header>

  <main class="container">
    {% with messages = get_flashed_messages(with_categories=true) %}
      {% if messages %}
        <div class="flash-list">
          {% for category, msg in messages %}
            <div class="flash {{ category }}">{{ msg }}</div>
          {% endfor %}
        </div>
      {% endif %}
    {% endwith %}

    <div class="form card">
      <h2>Add Contact</h2>
      <form method="post">
        <label>Name<br><input type="text" name="name" required></label>
        <label>Phone<br><input type="text" name="phone" required></label>
        <label>Email<br><input type="email" name="email" required></label>
        <div class="form-actions">
          <button type="submit">Add</button>
          <a class="button-link" href="{{ url_for('index') }}">Cancel</a>
        </div>
      </form>
    </div>
  </main>

  <footer class="site-footer">
    <div class="container">
      <p>© {{ year }} Contact Management System</p>
    </div>
  </footer>
</body>
</html>
"""

EDIT_HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Edit Contact - Contact Management System</title>
  <link rel="stylesheet" href="{{ url_for('styles') }}">
</head>
<body>
  <header class="site-header">
    <div class="container">
      <h1><a href="{{ url_for('index') }}">Contact Management System</a></h1>
      <nav>
        <a href="{{ url_for('index') }}">Home</a>
        <a href="{{ url_for('add_contact') }}">Add Contact</a>
      </nav>
    </div>
  </header>

  <main class="container">
    {% with messages = get_flashed_messages(with_categories=true) %}
      {% if messages %}
        <div class="flash-list">
          {% for category, msg in messages %}
            <div class="flash {{ category }}">{{ msg }}</div>
          {% endfor %}
        </div>
      {% endif %}
    {% endwith %}

    <div class="form card">
      <h2>Edit Contact</h2>
      <form method="post">
        <label>Name<br><input type="text" name="name" value="{{ contact.name }}" required></label>
        <label>Phone<br><input type="text" name="phone" value="{{ contact.phone }}" required></label>
        <label>Email<br><input type="email" name="email" value="{{ contact.email }}" required></label>
        <div class="form-actions">
          <button type="submit">Save</button>
          <a class="button-link" href="{{ url_for('index') }}">Cancel</a>
        </div>
      </form>

      <form method="post" action="{{ url_for('delete_contact', contact_id=contact.id) }}" onsubmit="return confirm('Delete this contact?');" style="margin-top:12px;">
        <button type="submit" class="danger">Delete Contact</button>
      </form>
    </div>
  </main>

  <footer class="site-footer">
    <div class="container">
      <p>© {{ year }} Contact Management System</p>
    </div>
  </footer>
</body>
</html>
"""

# --- Routes ---
@app.context_processor
def inject_year():
    return {"year": datetime.now().year}

@app.route("/", methods=["GET"])
def index():
    q = request.args.get("q", "").strip().lower()
    if q:
        filtered = [c for c in contacts if q in c.get("name", "").lower() or q in c.get("phone", "").lower()]
    else:
        filtered = contacts
    filtered = sorted(filtered, key=lambda x: x.get("id", 0), reverse=True)
    return render_template_string(INDEX_HTML, contacts=filtered, q=request.args.get("q", ""))

@app.route("/add", methods=["GET", "POST"])
def add_contact():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip()
        if not name or not phone or not email:
            flash("All fields are required.", "error")
            return redirect(url_for("add_contact"))
        new = {
            "id": next_id(),
            "name": name,
            "phone": phone,
            "email": email,
            "created": datetime.now().isoformat()
        }
        contacts.append(new)
        try:
            save_contacts(contacts)
        except Exception:
            flash("Could not save contacts to file.", "warning")
        flash("Contact added.", "success")
        return redirect(url_for("index"))
    return render_template_string(ADD_HTML)

@app.route("/edit/<int:contact_id>", methods=["GET", "POST"])
def edit_contact(contact_id):
    contact = next((c for c in contacts if c.get("id") == contact_id), None)
    if not contact:
        flash("Contact not found.", "error")
        return redirect(url_for("index"))
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip()
        if not name or not phone or not email:
            flash("All fields are required.", "error")
            return redirect(url_for("edit_contact", contact_id=contact_id))
        contact["name"] = name
        contact["phone"] = phone
        contact["email"] = email
        contact["updated"] = datetime.now().isoformat()
        try:
            save_contacts(contacts)
        except Exception:
            flash("Could not save contacts to file.", "warning")
        flash("Contact updated.", "success")
        return redirect(url_for("index"))
    return render_template_string(EDIT_HTML, contact=contact)

@app.route("/delete/<int:contact_id>", methods=["POST"])
def delete_contact(contact_id):
    global contacts
    before = len(contacts)
    contacts = [c for c in contacts if c.get("id") != contact_id]
    if len(contacts) < before:
        try:
            save_contacts(contacts)
        except Exception:
            flash("Could not save contacts to file.", "warning")
        flash("Contact deleted.", "success")
    else:
        flash("Contact not found.", "error")
    return redirect(url_for("index"))

# Serve CSS so no static folder is required
@app.route("/styles.css")
def styles():
    css = """
:root{--bg:#f7f7f8;--card:#fff;--accent:#2b6cb0;--muted:#6b7280;--maxw:900px}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);font-family:system-ui,Segoe UI,Roboto,Arial;color:#111;min-height:100vh;display:flex;flex-direction:column}
.container{width:92%;max-width:var(--maxw);margin:18px auto}
.site-header{background:linear-gradient(90deg,var(--accent),#4c9bd6);color:#fff;padding:14px 0}
.site-header .container{display:flex;justify-content:space-between;align-items:center}
.site-header a{color:#fff;text-decoration:none;margin-left:12px}
nav a{margin-left:12px}
.site-footer{margin-top:auto;text-align:center;padding:12px 0;color:var(--muted);font-size:.9rem}
.flash-list{margin:12px 0}
.flash{padding:8px 12px;border-radius:6px;margin-bottom:8px}
.flash.success{background:#e6fffa;color:#065f46}
.flash.error{background:#ffe6e6;color:#7a1f1f}
.flash.warning{background:#fff7e6;color:#7a4f00}
.toolbar{margin:12px 0;display:flex;justify-content:space-between;align-items:center}
.search-form input[type="text"]{padding:8px;border-radius:6px;border:1px solid #ddd;width:260px}
.search-form button{padding:8px 10px;margin-left:8px;border-radius:6px;border:0;background:var(--accent);color:#fff}
.search-form .clear{margin-left:8px;color:var(--muted);text-decoration:none}
.contacts-table{width:100%;border-collapse:collapse;background:var(--card);border-radius:8px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,0.06)}
.contacts-table th, .contacts-table td{padding:12px;border-bottom:1px solid #f1f1f1;text-align:left}
.contacts-table th{background:#fafafa;color:var(--muted);font-weight:600}
.actions a{margin-right:8px;color:var(--accent);text-decoration:none}
.link-button{background:none;border:0;color:var(--accent);cursor:pointer;padding:0}
.form{background:var(--card);padding:16px;border-radius:8px;box-shadow:0 1px 3px rgba(0,0,0,0.06)}
.form label{display:block;margin-bottom:10px}
.form input, .form textarea{width:100%;padding:8px;border:1px solid #ddd;border-radius:6px}
.form-actions{margin-top:12px}
.form-actions button{background:var(--accent);color:#fff;padding:8px 12px;border-radius:6px;border:0}
.button-link{display:inline-block;padding:8px 12px;background:#eee;border-radius:6px;color:#333;text-decoration:none;margin-left:8px}
.danger{background:#d9534f;color:#fff;padding:8px 12px;border-radius:6px;border:0}
.card{background:var(--card);padding:16px;border-radius:8px;box-shadow:0 1px 3px rgba(0,0,0,0.06)}
@media (max-width:600px){
  .site-header .container{flex-direction:column;gap:8px}
  .search-form input[type="text"]{width:100%}
}
"""
    return app.response_class(css, mimetype="text/css")

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
