from sqlalchemy import Column, String, Integer, Numeric, DateTime, Text, ForeignKey, Boolean, BigInteger
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), unique=True, index=True, nullable=False)  # Retail Pro userID
    email = Column(String(255), unique=True, index=True, nullable=True)
    password_hash = Column(String(255), nullable=True)
    api_key_hash = Column(String(255), nullable=True)  # hash of the long-term Bearer token
    claude_key_encrypted = Column(Text, nullable=True)
    claude_model = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class OnboardingToken(Base):
    __tablename__ = "onboarding_tokens"
    token = Column(String(128), primary_key=True)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)

class Subsidiary(Base):
    __tablename__ = "subsidiaries"
    id = Column(Integer, primary_key=True)
    user_id = Column(String(50), ForeignKey("users.user_id"), index=True)
    sbssid = Column(String(30), index=True)
    sbsno = Column(Integer)
    sbsname = Column(String(255))
    currencycode = Column(String(10))

class Store(Base):
    __tablename__ = "stores"
    id = Column(Integer, primary_key=True)
    user_id = Column(String(50), ForeignKey("users.user_id"), index=True)
    storesid = Column(String(30), index=True)
    sbsno = Column(Integer)
    storeno = Column(Integer)
    storecode = Column(String(10))
    storename = Column(String(255))
    address1 = Column(String(255))
    address2 = Column(String(255))
    address3 = Column(String(255))
    address4 = Column(String(255))
    address5 = Column(String(255))
    address6 = Column(String(255))
    zip = Column(String(20))

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True)
    user_id = Column(String(50), ForeignKey("users.user_id"), index=True)
    sid = Column(String(30), index=True)  # item SID
    sku = Column(String(50))
    description = Column(String(255))
    # add other item fields as needed

class Inventory(Base):
    __tablename__ = "inventory"
    id = Column(Integer, primary_key=True)
    user_id = Column(String(50), index=True)
    sid = Column(String(30), index=True)          # item SID
    qtystoresid = Column(String(30), index=True)  # store SID
    qtysbssid = Column(String(30), index=True)    # subsidiary SID
    qtyqty = Column(Numeric(12, 2))

class OpenPO(Base):
    __tablename__ = "open_pos"
    id = Column(Integer, primary_key=True)
    user_id = Column(String(50), index=True)
    sid = Column(String(30), index=True)          # item SID
    storesid = Column(String(30), index=True)
    sbssid = Column(String(30), index=True)
    qty_on_order = Column(Numeric(12, 2))
    po_number = Column(String(50))

class SalesDocument(Base):
    __tablename__ = "sales_documents"
    id = Column(Integer, primary_key=True)
    user_id = Column(String(50), index=True)
    sid = Column(String(30), index=True)  # document ID
    bt_cuid = Column(String(50))
    subsidiary_number = Column(String(20))
    store_number = Column(String(20))
    sold_qty = Column(Numeric(12, 2))
    return_qty = Column(Numeric(12, 2))
    order_qty = Column(Numeric(12, 2))
    status = Column(String(10))
    receipt_type = Column(String(10))
    order_type = Column(String(20))
    transaction_subtotal = Column(Numeric(14, 2))
    sale_total_tax_amt = Column(Numeric(14, 2))
    transaction_total_amt = Column(Numeric(14, 2))
    created_datetime = Column(DateTime)
    modified_datetime = Column(DateTime)
    document_number = Column(String(50))
    workstation_name = Column(String(100))

class SalesLine(Base):
    __tablename__ = "sales_lines"
    id = Column(Integer, primary_key=True)
    document_sid = Column(String(30), index=True)
    user_id = Column(String(50), index=True)
    invn_sbs_item_sid = Column(String(30), index=True)  # item SID
    quantity = Column(Numeric(12, 2))
    price = Column(Numeric(12, 2))
    original_price = Column(Numeric(12, 2))
    cost = Column(Numeric(12, 2))
    total_discount_amount = Column(Numeric(12, 2))
    item_type = Column(String(10))
    upc = Column(String(50))
    alu = Column(String(50))
