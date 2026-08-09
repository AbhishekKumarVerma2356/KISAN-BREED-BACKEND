import json
import os

from fastapi import APIRouter, HTTPException


router = APIRouter(
    tags=["Home"]
)


# =========================================================
# DATA FOLDER
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATA_FOLDER = os.path.join(
    BASE_DIR,
    "data"
)


# =========================================================
# READ JSON HELPER
# =========================================================

def read_json(filename: str):

    file_path = os.path.join(
        DATA_FOLDER,
        filename
    )

    print("Reading file:", file_path)

    if not os.path.exists(file_path):

        raise HTTPException(
            status_code=404,
            detail=f"Data file not found: {filename}"
        )

    try:

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except json.JSONDecodeError:

        raise HTTPException(
            status_code=500,
            detail=f"Invalid JSON: {filename}"
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =========================================================
# SITE
# =========================================================

@router.get("/site")
def get_site():

    return read_json("site.json")


# =========================================================
# TESTIMONIALS
# =========================================================

@router.get("/testimonials")
def get_testimonials():

    return read_json("testimonials.json")


# =========================================================
# FAQS
# =========================================================

@router.get("/faqs")
def get_faqs():

    return read_json("faqs.json")


# =========================================================
# GALLERY
# =========================================================

@router.get("/gallery")
def get_gallery():

    return read_json("gallery.json")


# =========================================================
# CERTIFICATES
# =========================================================

@router.get("/certificates")
def get_certificates():

    return read_json("certificates.json")