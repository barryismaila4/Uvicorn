from sanic import Sanic # type: ignore
from sanic.response import json # type: ignore
from sanic_cors import CORS # type: ignore
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DECIMAL # type: ignore
from sqlalchemy.ext.declarative import declarative_base # type: ignore
from sqlalchemy.orm import sessionmaker, Session # type: ignore
from pydantic import BaseModel
import uvicorn

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

# Initialisation de Sanic
app = Sanic("ecommerce_app")
CORS(app)  # Permet CORS pour toutes les routes

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
@app.post("/users/")
async def create_user(request):
    data = request.json
    db = next(get_db())
    db_user = User(username=data["username"], email=data["email"])
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return json({"username": db_user.username, "email": db_user.email}, status=201)

# Routes pour gérer les catégories
@app.post("/categories/")
async def create_category(request):
    data = request.json
    db = next(get_db())
    db_category = Category(name=data["name"])
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return json({"name": db_category.name}, status=201)

# Routes pour gérer les produits
@app.post("/products/")
async def create_product(request):
    data = request.json
    db = next(get_db())
    db_product = Product(name=data["name"], description=data["description"], price=data["price"], category_id=data["category_id"])
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return json({"name": db_product.name, "description": db_product.description, "price": db_product.price}, status=201)

# Routes pour gérer le panier
@app.post("/cart/")
async def add_to_cart(request):
    data = request.json
    db = next(get_db())
    db_cart_item = Cart(user_id=1, product_id=data["product_id"], quantity=data["quantity"])  # Simplification pour l'exemple
    db.add(db_cart_item)
    db.commit()
    db.refresh(db_cart_item)
    return json({"product_id": db_cart_item.product_id, "quantity": db_cart_item.quantity}, status=201)

# Initialisation des tables
Base.metadata.create_all(bind=engine)

# Exécution du serveur
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000)
