from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DECIMAL # type: ignore
from sqlalchemy.ext.declarative import declarative_base # type: ignore
from sqlalchemy.orm import sessionmaker # type: ignore
from sqlalchemy.orm import Session # type: ignore
from fastapi.middleware.cors import CORSMiddleware

# Configuration de la base de données MySQL
DATABASE_URL = "mysql+mysqlconnector://root:AA0556563a@localhost/ecommerce"

# Création de la base et du moteur
engine = create_engine(DATABASE_URL, pool_recycle=3600)
Base = declarative_base()

# Session locale pour interagir avec la base
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Modèle de données
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    email = Column(String, unique=True, index=True)

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    price = Column(DECIMAL)
    category_id = Column(Integer, ForeignKey("categories.id"))

class Cart(Base):
    __tablename__ = "cart"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer)

# Initialisation de FastAPI
app = FastAPI()

# Ajouter CORS pour accepter toutes les origines
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permet toutes les origines
    allow_credentials=True,
    allow_methods=["*"],  # Permet toutes les méthodes
    allow_headers=["*"],  # Permet tous les en-têtes
)

# Modèles Pydantic pour les réponses
class UserCreate(BaseModel):
    username: str
    email: str

class CategoryCreate(BaseModel):
    name: str

class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    category_id: int

class CartItem(BaseModel):
    product_id: int
    quantity: int

# Fonction pour récupérer une session de base de données
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Routes pour gérer les utilisateurs
@app.post("/users/", response_model=UserCreate)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(username=user.username, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/{user_id}", response_model=UserCreate)
def get_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# Routes pour gérer les catégories
@app.post("/categories/", response_model=CategoryCreate)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    db_category = Category(name=category.name)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@app.get("/categories/", response_model=List[CategoryCreate])
def get_categories(db: Session = Depends(get_db)):
    return db.query(Category).all()

# Routes pour gérer les produits
@app.post("/products/", response_model=ProductCreate)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    db_product = Product(name=product.name, description=product.description, price=product.price, category_id=product.category_id)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@app.get("/products/", response_model=List[ProductCreate])
def get_products(db: Session = Depends(get_db)):
    return db.query(Product).all()

# Routes pour gérer le panier
@app.post("/cart/", response_model=List[CartItem])
def add_to_cart(cart_item: CartItem, db: Session = Depends(get_db)):
    db_cart_item = Cart(user_id=1, product_id=cart_item.product_id, quantity=cart_item.quantity)  # Simplification pour l'exemple
    db.add(db_cart_item)
    db.commit()
    db.refresh(db_cart_item)
    return db.query(Cart).filter(Cart.user_id == 1).all()  # Retourne tous les éléments du panier de l'utilisateur

@app.get("/cart/", response_model=List[CartItem])
def get_cart(db: Session = Depends(get_db)):
    return db.query(Cart).filter(Cart.user_id == 1).all()

# Initialisation des tables
Base.metadata.create_all(bind=engine)

# Pour exécuter : uvicorn main:app --reload
