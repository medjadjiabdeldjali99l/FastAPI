import uvicorn
from fastapi import FastAPI
from Routes import router
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from database import OdooDatabase
from datetime import datetime


app = FastAPI(
    title="Mon API Errafik",
    description="API protégée par token",
)


API_VERSION = "v1.0.13"
RELEASE_DATE = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@app.on_event("startup")
def startup_event():
    app.state.odooDatabase = OdooDatabase()  # Assure-toi que cette classe est définie quelque part

def get_odoo_database():
    return app.state.odooDatabase
    
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router=router)

@app.get("/")
def read_root():
    return {
        "Status": "success",
        "title": "Miniros Secured API",
    }

@app.get("/version")
def reed_version():
    return {
        "version": API_VERSION,
        "date": RELEASE_DATE,
    }

# if __name__ == '__main__':
#     uvicorn.run(f"main:app", host="192.168.100.2", port=8888, reload=True)
