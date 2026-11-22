from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel

from database import get_db, engine, Base, settings
import models
import schemas
import security

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="MMA Server", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://mmanalyticsnow.com",
        "https://www.mmanalyticsnow.com",
        "https://mmanalytics-web.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def get_current_user(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = authorization.split(" ", 1)[1]
    token_hash = security.hash_api_key(token)
    user = db.query(models.User).filter(models.User.api_key_hash == token_hash).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user

# ---------------------------------------------------------------------------
# Login (for dashboard)
# ---------------------------------------------------------------------------
class LoginRequest(BaseModel):
    email: str
    password: str

@app.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == payload.email).first()
    if not user or not user.password_hash:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not security.verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Issue a fresh long-term token for the session
    plain_token = security.create_long_term_token(user.user_id)
    user.api_key_hash = security.hash_api_key(plain_token)
    db.commit()

    return {"status": "ok", "token": plain_token}

# ---------------------------------------------------------------------------
# Dashboard endpoints
# ---------------------------------------------------------------------------
@app.get("/dashboard/summary")
def dashboard_summary(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Placeholder values — replace with real calculations later
    return {
        "total_sales": "$0.00",
        "units_sold": 0,
        "stockout_risks": 0,
        "excess_inventory": 0
    }

@app.get("/dashboard/recommendations")
def dashboard_recommendations(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Placeholder — return empty list for now
    return []

# ---------------------------------------------------------------------------
# Ask AI
# ---------------------------------------------------------------------------
class AskRequest(BaseModel):
    question: str

@app.post("/ask")
def ask_ai(payload: AskRequest, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Placeholder response. Later this will call Claude with the user's key and data context.
    return {
        "answer": f"You asked: “{payload.question}”. AI responses will appear here once Claude integration is connected."
    }

# ---------------------------------------------------------------------------
# Onboarding
# ---------------------------------------------------------------------------
@app.get("/onboard/token", response_model=schemas.OnboardTokenResponse)
def get_onboarding_token(db: Session = Depends(get_db)):
    token = security.create_onboarding_token()
    expires = datetime.utcnow() + timedelta(minutes=settings.onboarding_token_expire_minutes)
    db_token = models.OnboardingToken(token=token, expires_at=expires)
    db.add(db_token)
    db.commit()
    return {"token": token, "expires_in": settings.onboarding_token_expire_minutes * 60}

@app.post("/onboard", response_model=schemas.StandardResponse)
def onboard(payload: schemas.OnboardPayload, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.user_id == payload.userID).first()
    if not user:
        user = models.User(user_id=payload.userID)
        db.add(user)
        db.flush()

    if payload.storecode:
        user.storecode = payload.storecode

    plain_token = security.create_long_term_token(payload.userID)
    user.api_key_hash = security.hash_api_key(plain_token)
    db.commit()

    return {"status": "ok", "token": plain_token, "message": "Account created/updated"}

# ---------------------------------------------------------------------------
# Main upload endpoint
# ---------------------------------------------------------------------------
@app.post("/upload", response_model=schemas.StandardResponse)
def upload(
    payload: schemas.UploadPayload,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if payload.userID != user.user_id:
        raise HTTPException(status_code=403, detail="userID does not match token")

    upload_type = payload.uploadType.lower()

    if upload_type == "subsidiaries":
        _handle_subsidiaries(payload, user, db)
    elif upload_type == "stores":
        _handle_stores(payload, user, db)
    elif upload_type == "items":
        _handle_items(payload, user, db)
    elif upload_type == "inventory":
        _handle_inventory(payload, user, db)
    elif upload_type == "open_pos":
        _handle_open_pos(payload, user, db)
    elif upload_type == "sales":
        _handle_sales(payload, user, db)
    elif upload_type == "logins":
        _handle_logins(payload, user, db)
    else:
        return {"status": "error", "message": f"Unknown uploadType: {payload.uploadType}"}

    db.commit()
    return {"status": "ok", "message": f"Processed {upload_type}"}

# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------
def _handle_subsidiaries(payload, user, db):
    for row in payload.data or []:
        existing = db.query(models.Subsidiary).filter_by(
            user_id=user.user_id, sbssid=row.get("sbssid")
        ).first()
        if existing:
            existing.sbsno = row.get("sbsno")
            existing.sbsname = row.get("sbsname")
            existing.currencycode = row.get("currencycode")
        else:
            db.add(models.Subsidiary(
                user_id=user.user_id,
                sbssid=row.get("sbssid"),
                sbsno=row.get("sbsno"),
                sbsname=row.get("sbsname"),
                currencycode=row.get("currencycode")
            ))

def _handle_stores(payload, user, db):
    for row in payload.data or []:
        existing = db.query(models.Store).filter_by(
            user_id=user.user_id, storesid=row.get("storesid")
        ).first()
        if existing:
            for field in ["sbsno", "storeno", "storecode", "storename",
                          "address1", "address2", "address3", "address4",
                          "address5", "address6", "zip"]:
                setattr(existing, field, row.get(field))
        else:
            db.add(models.Store(user_id=user.user_id, **{k: row.get(k) for k in [
                "storesid", "sbsno", "storeno", "storecode", "storename",
                "address1", "address2", "address3", "address4", "address5", "address6", "zip"
            ]}))

def _to_decimal(val):
    if val is None or val == "":
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None

def _handle_items(payload, user, db):
    for row in payload.data or []:
        existing = db.query(models.Item).filter_by(
            user_id=user.user_id, sid=row.get("sid")
        ).first()
        fields = {
            "sku": row.get("sku"),
            "upc": row.get("upc"),
            "alu": row.get("alu"),
            "description1": row.get("description1"),
            "description2": row.get("description2"),
            "vendorcode": row.get("vendorcode"),
            "dcscode": row.get("dcscode"),
            "sbsno": row.get("sbsno"),
            "stylesid": str(row.get("stylesid")) if row.get("stylesid") is not None else None,
            "noninventory": row.get("noninventory"),
            "orderable": row.get("orderable"),
            "kittype": row.get("kittype"),
            "cost": _to_decimal(row.get("cost")),
            "price": _to_decimal(row.get("price")),
            "lastsolddate": row.get("lastsolddate"),
            "lastrcvddate": row.get("lastrcvddate"),
            "lastrcvdcost": _to_decimal(row.get("lastrcvdcost")),
        }
        if existing:
            for k, v in fields.items():
                setattr(existing, k, v)
        else:
            db.add(models.Item(user_id=user.user_id, sid=row.get("sid"), **fields))

def _handle_inventory(payload, user, db):
    for row in payload.data or []:
        existing = db.query(models.Inventory).filter_by(
            user_id=user.user_id,
            sid=row.get("sid"),
            qtystoresid=row.get("qtystoresid"),
            qtysbssid=row.get("qtysbssid")
        ).first()
        if existing:
            existing.qtyqty = row.get("qtyqty")
        else:
            db.add(models.Inventory(
                user_id=user.user_id,
                sid=row.get("sid"),
                qtystoresid=row.get("qtystoresid"),
                qtysbssid=row.get("qtysbssid"),
                qtyqty=row.get("qtyqty")
            ))

def _handle_open_pos(payload, user, db):
    for row in payload.data or []:
        db.add(models.OpenPO(
            user_id=user.user_id,
            sid=row.get("sid"),
            storesid=row.get("storesid") or row.get("qtystoresid"),
            sbssid=row.get("sbssid") or row.get("qtysbssid"),
            qty_on_order=row.get("qty_on_order") or row.get("qtyqty"),
            po_number=row.get("po_number")
        ))

def _handle_sales(payload, user, db):
    for doc in payload.data or []:
        existing = db.query(models.SalesDocument).filter_by(
            user_id=user.user_id, sid=doc.get("sid")
        ).first()
        if not existing:
            existing = models.SalesDocument(user_id=user.user_id, sid=doc.get("sid"))
            db.add(existing)
        for field in ["bt_cuid", "subsidiary_number", "store_number", "sold_qty",
                      "return_qty", "order_qty", "status", "receipt_type", "order_type",
                      "transaction_subtotal", "sale_total_tax_amt", "transaction_total_amt",
                      "document_number", "workstation_name"]:
            setattr(existing, field, doc.get(field))
        for dt_field in ["created_datetime", "modified_datetime"]:
            if doc.get(dt_field):
                try:
                    setattr(existing, dt_field, datetime.fromisoformat(doc[dt_field].replace("Z", "+00:00")))
                except Exception:
                    pass
        db.flush()
        db.query(models.SalesLine).filter_by(
            user_id=user.user_id, document_sid=doc.get("sid")
        ).delete()
        for line in doc.get("items") or []:
            db.add(models.SalesLine(
                document_sid=doc.get("sid"),
                user_id=user.user_id,
                invn_sbs_item_sid=line.get("invn_sbs_item_sid"),
                quantity=line.get("quantity"),
                price=line.get("price"),
                original_price=line.get("original_price"),
                cost=line.get("cost"),
                total_discount_amount=line.get("total_discount_amount"),
                item_type=line.get("item_type"),
                upc=line.get("upc"),
                alu=line.get("alu")
            ))

def _handle_logins(payload, user, db):
    for row in payload.data or []:
        # Nested format: {"logins": [{"username": "...", "password": "..."}]}
        logins = row.get("logins") or []
        for login in logins:
            username = login.get("username") or login.get("email")
            password = login.get("password")
            if username:
                # strip trailing = if present
                user.email = username.rstrip("=")
            if password:
                user.password_hash = security.hash_password(password.rstrip("="))

        # Flat format fallback
        if row.get("email"):
            user.email = row.get("email").rstrip("=")
        if row.get("password"):
            user.password_hash = security.hash_password(row.get("password").rstrip("="))

        if row.get("claudeKey"):
            user.claude_key_encrypted = security.encrypt_claude_key(row.get("claudeKey"))
        if row.get("claudeModel"):
            user.claude_model = row.get("claudeModel")

@app.get("/health")
def health():
    return {"status": "ok"}
