from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DECIMAL # type: ignore
from sqlalchemy.ext.declarative import declarative_base # type: ignore
from sqlalchemy.orm import sessionmaker, Session # type: ignore
from pydantic import BaseModel
import uvicorn
from typing import List

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

# Initialisation de Starlette
app = Starlette(debug=True)

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
@app.route("/users/", methods=["POST"])
async def create_user(request):
    data = await request.json()
    db = next(get_db())
    db_user = User(username=data["username"], email=data["email"])
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return JSONResponse({"username": db_user.username, "email": db_user.email}, status_code=201)

@app.route("/users/{user_id}", methods=["GET"])
async def get_user(request):
    user_id = int(request.path_params["user_id"])
    db = next(get_db())
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        return JSONResponse({"error": "User not found"}, status_code=404)
    return JSONResponse({"username": db_user.username, "email": db_user.email})

# Routes pour gérer les catégories
@app.route("/categories/", methods=["POST"])
async def create_category(request):
    data = await request.json()
    db = next(get_db())
    db_category = Category(name=data["name"])
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return JSONResponse({"name": db_category.name}, status_code=201)

@app.route("/categories/", methods=["GET"])
async def get_categories(request):
    db = next(get_db())
    categories = db.query(Category).all()
    return JSONResponse([{"id": c.id, "name": c.name} for c in categories])

# Routes pour gérer les produits
@app.route("/products/", methods=["POST"])
async def create_product(request):
    data = await request.json()
    db = next(get_db())
    db_product = Product(name=data["name"], description=data["description"], price=data["price"], category_id=data["category_id"])
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return JSONResponse({"name": db_product.name, "description": db_product.description, "price": db_product.price}, status_code=201)

@app.route("/products/", methods=["GET"])
async def get_products(request):
    db = next(get_db())
    products = db.query(Product).all()
    return JSONResponse([{"id": p.id, "name": p.name, "description": p.description, "price": p.price} for p in products])

# Routes pour gérer le panier
@app.route("/cart/", methods=["POST"])
async def add_to_cart(request):
    data = await request.json()
    db = next(get_db())
    db_cart_item = Cart(user_id=1, product_id=data["product_id"], quantity=data["quantity"])  # Simplification pour l'exemple
    db.add(db_cart_item)
    db.commit()
    db.refresh(db_cart_item)
    return JSONResponse({"product_id": db_cart_item.product_id, "quantity": db_cart_item.quantity}, status_code=201)

@app.route("/cart/", methods=["GET"])
async def get_cart(request):
    db = next(get_db())
    cart_items = db.query(Cart).filter(Cart.user_id == 1).all()
    return JSONResponse([{"product_id": ci.product_id, "quantity": ci.quantity} for ci in cart_items])

# Initialisation des tables
Base.metadata.create_all(bind=engine)

# Exécution du serveur
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
