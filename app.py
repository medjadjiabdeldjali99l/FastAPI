import uvicorn
from fastapi import FastAPI
# from routes import router
from fastapi.middleware.cors import CORSMiddleware
from database import OdooDatabase

app = FastAPI(
    title="Mon API Errafik",
    description="API protégée par token",
)



def get_odoo_database():
    return app.state.odooDatabase 
    


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
        "Status": "Success",
        "Message": "Guerrout"
    }

# if __name__ == '__main__':
#     uvicorn.run(f"main:app", host="192.168.100.2", port=8888, reload=True)
