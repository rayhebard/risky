from fastapi import FastAPI


app = FastAPI(title="Backstop Retriever")


@app.get("/")
async def read_root():
    return {"message": "Welcome to Back Stop Retriever Service"}
