from app import db
from datetime import datetime, timezone
def now(): return datetime.now(timezone.utc)
class User(db.Model):
    __tablename__="users"
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100),nullable=False)
    email=db.Column(db.String(120),unique=True,nullable=False,index=True)
    role=db.Column(db.String(30),nullable=False,default="analyst")
    created_at=db.Column(db.DateTime(timezone=True),default=now,nullable=False)
    incidents=db.relationship("Incident",back_populates="reporter")
class Asset(db.Model):
    __tablename__="assets"
    id=db.Column(db.Integer,primary_key=True)
    asset_name=db.Column(db.String(120),nullable=False)
    asset_type=db.Column(db.String(50),nullable=False)
    ip_address=db.Column(db.String(45))
    owner=db.Column(db.String(100))
    criticality=db.Column(db.String(20),nullable=False,default="medium")
    created_at=db.Column(db.DateTime(timezone=True),default=now,nullable=False)
    incidents=db.relationship("Incident",back_populates="asset")
class Incident(db.Model):
    __tablename__="incidents"
    id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(160),nullable=False)
    description=db.Column(db.Text,nullable=False)
    incident_type=db.Column(db.String(50),nullable=False)
    severity=db.Column(db.String(20),nullable=False,default="medium")
    status=db.Column(db.String(20),nullable=False,default="open")
    source_ip=db.Column(db.String(45))
    reported_at=db.Column(db.DateTime(timezone=True),default=now,nullable=False)
    user_id=db.Column(db.Integer,db.ForeignKey("users.id"),nullable=False)
    asset_id=db.Column(db.Integer,db.ForeignKey("assets.id"),nullable=False)
    reporter=db.relationship("User",back_populates="incidents")
    asset=db.relationship("Asset",back_populates="incidents")
    updates=db.relationship("IncidentUpdate",back_populates="incident",cascade="all, delete-orphan")
    audit_logs=db.relationship("AuditLog",back_populates="incident",cascade="all, delete-orphan")
class IncidentUpdate(db.Model):
    __tablename__="incident_updates"
    id=db.Column(db.Integer,primary_key=True)
    incident_id=db.Column(db.Integer,db.ForeignKey("incidents.id"),nullable=False)
    note=db.Column(db.Text,nullable=False)
    new_status=db.Column(db.String(20))
    created_at=db.Column(db.DateTime(timezone=True),default=now,nullable=False)
    incident=db.relationship("Incident",back_populates="updates")
class AuditLog(db.Model):
    __tablename__="audit_logs"
    id=db.Column(db.Integer,primary_key=True)
    incident_id=db.Column(db.Integer,db.ForeignKey("incidents.id"),nullable=False)
    action=db.Column(db.String(80),nullable=False)
    actor=db.Column(db.String(120),nullable=False)
    detail=db.Column(db.Text)
    created_at=db.Column(db.DateTime(timezone=True),default=now,nullable=False)
    incident=db.relationship("Incident",back_populates="audit_logs")
