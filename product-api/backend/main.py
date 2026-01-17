from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from models import Product
from database import session, engine
import database_model
from sqlalchemy.orm import Session 

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods = ["*"],
)

database_model.Base.metadata.create_all(bind=engine)


@app.get("/")
def greet():
    return "Welcome to my Ecomerce app"

products = [
    Product(id=1, name="Phone", description="A smartphone", price=699.99, quantity=50),
    Product(id=2, name="Laptop", description="A powerful laptop", price=999.99, quantity=30),
    Product(id=3, name="Pen", description="A blue ink pen", price=1.99, quantity=100),
    Product(id=4,name="Specs" , description="A Eyewear" , price=2700.00, quantity=10)
]

def get_db():
    db = Session(bind=engine)
    print("✅ Session created:", db)
    print("📌 Session type:", type(db))
    print("🔗 Engine used:", engine)
    try:
        yield db
    finally:
        db.close()



def init_db():
    db = session()
    print("📌 db type:", type(db))

    count = db.query(database_model.Product).count()

    if count == 0:
        for product in products:
            db.add(database_model.Product(**product.model_dump()))
            print(product.model_dump())
        
    db.commit()

init_db()



@app.get("/products")
def get_all_products(db: Session = Depends(get_db)):
    print("📥 db received in API:", db)
    db_products = db.query(database_model.Product).all()
    print("📦 Products fetched:", db_products)
    return db_products

@app.get("/products/{id}")
def get_product_by_id(id: int, db: Session = Depends(get_db)):
    db_product = db.query(database_model.Product).filter(database_model.Product.id == id).first()
    if db_product:
        return db_product

    return "Product Not Found"


@app.post("/products")
def add_product(product: Product, db: Session = Depends(get_db)):
    db.add(database_model.Product(**product.model_dump()))
    db.commit()
    return product


@app.put("/products/{id}")
def update_product(id: int, product: Product, db: Session = Depends(get_db)):
    db_product = db.query(database_model.Product).filter(database_model.Product.id == id).first()

    if not db_product:
        return "Product not found"

    update_data = product.model_dump(exclude={"id"}, exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_product, key, value)

    db.commit()
    db.refresh(db_product)

    return db_product
    # for i in range(len(products)):
    #     if products[i].id == id:
    #         products[i] = product
    #         return "Product added sucessfully"
    
    # return "Product not found"

@app.delete("/products/{id}")
def delete_product(id: int, db: Session = Depends(get_db)):
    db_product = db.query(database_model.Product).filter(database_model.Product.id == id).first()
    if db_product:
        db.delete(db_product)
        db.commit()
        return "Product deleted"
    else:
        return "Product not found"    