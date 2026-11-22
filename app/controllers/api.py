from flask import Blueprint,request,jsonify
from sqlalchemy import or_
from app import db
from app.models import User,Asset,Incident,IncidentUpdate,AuditLog
api=Blueprint("api",__name__)
SEV={"low","medium","high","critical"}; STATUS={"open","investigating","contained","resolved","closed"}
def err(msg,code="VALIDATION_ERROR",status=400):
    return jsonify({"success":False,"error":{"code":code,"message":msg}}),status
def out(i):
    return {"id":i.id,"title":i.title,"description":i.description,"incident_type":i.incident_type,
      "severity":i.severity,"status":i.status,"source_ip":i.source_ip,"reported_at":i.reported_at.isoformat(),
      "reporter":{"id":i.reporter.id,"name":i.reporter.name},"asset":{"id":i.asset.id,"asset_name":i.asset.asset_name}}
@api.get("/health")
def health(): return jsonify({"success":True,"data":{"status":"ok"}})
@api.post("/users")
def add_user():
    d=request.get_json(silent=True) or {}; n=d.get("name"); e=d.get("email","").lower()
    if not n or "@" not in e: return err("name dan email valid wajib diisi")
    if User.query.filter_by(email=e).first(): return err("Email sudah terdaftar","DUPLICATE_EMAIL",409)
    u=User(name=n.strip(),email=e,role=d.get("role","analyst")); db.session.add(u); db.session.commit()
    return jsonify({"success":True,"data":{"id":u.id,"name":u.name,"email":u.email,"role":u.role}}),201
@api.get("/users")
def users():
    return jsonify({"success":True,"data":[{"id":u.id,"name":u.name,"email":u.email,"role":u.role} for u in User.query.all()]})
@api.post("/assets")
def add_asset():
    d=request.get_json(silent=True) or {}
    if not d.get("asset_name") or not d.get("asset_type"): return err("asset_name dan asset_type wajib diisi")
    c=d.get("criticality","medium")
    if c not in SEV: return err("criticality tidak valid")
    a=Asset(asset_name=d["asset_name"].strip(),asset_type=d["asset_type"],ip_address=d.get("ip_address"),owner=d.get("owner"),criticality=c)
    db.session.add(a); db.session.commit()
    return jsonify({"success":True,"data":{"id":a.id,"asset_name":a.asset_name}}),201
@api.get("/assets")
def assets():
    return jsonify({"success":True,"data":[{"id":a.id,"asset_name":a.asset_name,"asset_type":a.asset_type,"ip_address":a.ip_address,"criticality":a.criticality} for a in Asset.query.all()]})
@api.post("/incidents")
def add_incident():
    d=request.get_json(silent=True) or {}; req=["title","description","incident_type","user_id","asset_id"]
    missing=[k for k in req if d.get(k) in (None,"")]
    if missing: return err("Field wajib: "+", ".join(missing))
    sev=d.get("severity","medium")
    if sev not in SEV: return err("severity tidak valid")
    u=db.session.get(User,d["user_id"]); a=db.session.get(Asset,d["asset_id"])
    if not u or not a: return err("user_id atau asset_id tidak ditemukan","RELATED_RESOURCE_NOT_FOUND",404)
    i=Incident(title=d["title"].strip(),description=d["description"].strip(),incident_type=d["incident_type"],severity=sev,source_ip=d.get("source_ip"),user_id=u.id,asset_id=a.id)
    db.session.add(i); db.session.flush()
    db.session.add(AuditLog(incident_id=i.id,action="incident_created",actor=u.email,detail="Insiden dibuat"))
    db.session.commit(); return jsonify({"success":True,"data":out(i)}),201
@api.get("/incidents")
def incidents():
    q=Incident.query; s=request.args.get("search","").strip()
    if s:
        like=f"%{s}%"; q=q.filter(or_(Incident.title.ilike(like),Incident.description.ilike(like),Incident.incident_type.ilike(like)))
    sev=request.args.get("severity"); st=request.args.get("status")
    if sev:
        if sev not in SEV:return err("Filter severity tidak valid")
        q=q.filter_by(severity=sev)
    if st:
        if st not in STATUS:return err("Filter status tidak valid")
        q=q.filter_by(status=st)
    page=max(request.args.get("page",1,type=int),1); per=min(max(request.args.get("per_page",10,type=int),1),100)
    p=q.order_by(Incident.reported_at.desc()).paginate(page=page,per_page=per,error_out=False)
    return jsonify({"success":True,"data":[out(i) for i in p.items],"meta":{"page":page,"per_page":per,"total":p.total,"pages":p.pages}})
@api.get("/incidents/<int:iid>")
def detail(iid):
    i=db.session.get(Incident,iid)
    if not i:return err("Insiden tidak ditemukan","NOT_FOUND",404)
    return jsonify({"success":True,"data":out(i)})
@api.patch("/incidents/<int:iid>")
def update(iid):
    i=db.session.get(Incident,iid)
    if not i:return err("Insiden tidak ditemukan","NOT_FOUND",404)
    d=request.get_json(silent=True) or {}
    if "severity" in d:
        if d["severity"] not in SEV:return err("severity tidak valid")
        i.severity=d["severity"]
    if "status" in d:
        if d["status"] not in STATUS:return err("status tidak valid")
        i.status=d["status"]
    if "title" in d:
        if not str(d["title"]).strip():return err("title tidak boleh kosong")
        i.title=d["title"].strip()
    db.session.add(AuditLog(incident_id=i.id,action="incident_updated",actor=d.get("actor","system"),detail=str(d)))
    db.session.commit();return jsonify({"success":True,"data":out(i)})
@api.delete("/incidents/<int:iid>")
def delete(iid):
    i=db.session.get(Incident,iid)
    if not i:return err("Insiden tidak ditemukan","NOT_FOUND",404)
    db.session.delete(i);db.session.commit();return jsonify({"success":True,"message":"Insiden berhasil dihapus"})
@api.post("/incidents/<int:iid>/updates")
def add_update(iid):
    i=db.session.get(Incident,iid)
    if not i:return err("Insiden tidak ditemukan","NOT_FOUND",404)
    d=request.get_json(silent=True) or {}
    if not d.get("note"):return err("note wajib diisi")
    st=d.get("new_status")
    if st and st not in STATUS:return err("status tidak valid")
    u=IncidentUpdate(incident_id=i.id,note=d["note"],new_status=st)
    if st:i.status=st
    db.session.add(u);db.session.add(AuditLog(incident_id=i.id,action="update_added",actor=d.get("actor","system"),detail=d["note"]))
    db.session.commit();return jsonify({"success":True,"data":{"id":u.id,"incident_id":i.id,"note":u.note,"new_status":u.new_status}}),201
@api.get("/incidents/<int:iid>/updates")
def updates(iid):
    if not db.session.get(Incident,iid):return err("Insiden tidak ditemukan","NOT_FOUND",404)
    rows=IncidentUpdate.query.filter_by(incident_id=iid).order_by(IncidentUpdate.created_at.desc()).all()
    return jsonify({"success":True,"data":[{"id":u.id,"note":u.note,"new_status":u.new_status,"created_at":u.created_at.isoformat()} for u in rows]})
@api.get("/audit-logs")
def logs():
    rows=AuditLog.query.order_by(AuditLog.created_at.desc()).limit(100).all()
    return jsonify({"success":True,"data":[{"id":x.id,"incident_id":x.incident_id,"action":x.action,"actor":x.actor,"detail":x.detail,"created_at":x.created_at.isoformat()} for x in rows]})
