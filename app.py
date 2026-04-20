from fastapi import FastAPI
from pydantic import BaseModel

from db import activate_license, get_license


app = FastAPI(title="GCleaner License API")


class LicensePayload(BaseModel):
    license_key: str
    hwid_hash: str


@app.get("/")
def root():
    return {"ok": True, "service": "gcleaner-license-api"}


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/activate")
def activate(payload: LicensePayload):
    return activate_license(payload.license_key.strip(), payload.hwid_hash.strip())


@app.post("/validate")
def validate(payload: LicensePayload):
    return activate_license(payload.license_key.strip(), payload.hwid_hash.strip())


@app.get("/license/{license_key}")
def license_info(license_key: str):
    data = get_license(license_key.strip())
    if not data:
        return {"status": "invalid", "message": "License not found"}
    return data
