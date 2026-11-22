from app import create_app,db
app=create_app()
@app.cli.command("init-db")
def init_db():
    db.create_all();print("Database dibuat.")
@app.cli.command("seed")
def seed():
    from app.models import User,Asset,Incident
    db.create_all()
    if not User.query.first():
        u=User(name="Admin SOC",email="admin@example.com",role="admin")
        a=Asset(asset_name="Web Server Utama",asset_type="server",ip_address="192.0.2.10",owner="Tim Infrastruktur",criticality="critical")
        db.session.add_all([u,a]);db.session.flush()
