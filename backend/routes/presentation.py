from fastapi import APIRouter
from bson import ObjectId
from services.ppt_service import create_ppt
from models.outline import OutlineUpdate
import json

from config import presentations_collection
from models.presentation import PresentationCreate
from models.outline import OutlineUpdate
from services.gemini_service import (
    generate_outline,
    generate_all_slide_content
)


router = APIRouter(
    prefix="/presentations",
    tags=["Presentations"]
)


@router.post("/create")
def create_presentation(data: PresentationCreate):

    presentation = {
        "topic": data.topic,
        "purpose": data.purpose,
        "audience": data.audience,
        
        "template_name": None,
        "theme": None,

        "slides": [],

        "outline": [],
        "outline_approved": False
       
    }

    result = presentations_collection.insert_one(presentation)

    return {
        "status": "success",
        "presentation_id": str(result.inserted_id)
    }


@router.get("/{presentation_id}")
def get_presentation(presentation_id: str):

    try:
        presentation = presentations_collection.find_one(
            {"_id": ObjectId(presentation_id)}
        )

        if not presentation:
            return {"error": "Presentation not found"}

        presentation["_id"] = str(presentation["_id"])

        return presentation

    except Exception as e:
        return {"error": str(e)}


@router.post("/{presentation_id}/generate-outline")
def generate_presentation_outline(presentation_id: str):

    presentation = presentations_collection.find_one(
        {"_id": ObjectId(presentation_id)}
    )

    if not presentation:
        return {
            "error": "Presentation not found"
        }

    outline_text = generate_outline(
        presentation["topic"],
        presentation["purpose"],
        presentation["audience"]
    )

    lines = [
        line.strip()
        for line in outline_text.split("\n")
        if line.strip()
    ]

    outline = []

    for index, line in enumerate(lines, start=1):

        title = line

        if ". " in line:
            title = line.split(". ", 1)[1]

        outline.append({
            "id": index,
            "title": title
        })

    presentations_collection.update_one(
        {"_id": ObjectId(presentation_id)},
        {
            "$set": {
                "outline": outline
            }
        }
    )

    return {
        "status": "success",
        "outline": outline
    }


@router.put("/{presentation_id}/outline")
def update_outline(
    presentation_id: str,
    data: OutlineUpdate
):

    presentations_collection.update_one(
        {"_id": ObjectId(presentation_id)},
        {
            "$set": {
                "outline": [
                    item.model_dump()
                    for item in data.outline
                ]
            }
        }
    )

    return {
        "status": "success",
        "message": "Outline updated"
    }
    
@router.post("/{presentation_id}/approve-outline")
def approve_outline(presentation_id: str):

    presentations_collection.update_one(
        {"_id": ObjectId(presentation_id)},
        {
            "$set": {
                "outline_approved": True,
                "status": "outline_approved"
            }
        }
    )

    return {
        "status": "success",
        "message": "Outline approved"
    }

@router.post("/{presentation_id}/generate-content")
def generate_content(presentation_id: str):

    presentation = presentations_collection.find_one(
        {"_id": ObjectId(presentation_id)}
    )

    if not presentation:
        return {"error": "Presentation not found"}

    if not presentation.get("outline_approved"):
        return {
            "error": "Outline must be approved first"
        }

    content_text = generate_all_slide_content(
    presentation["outline"]
)

    content_text = content_text.strip()

    slides_data = json.loads(content_text)

    slides = slides_data["slides"]

    presentations_collection.update_one(
        {"_id": ObjectId(presentation_id)},
        {
            "$set": {
                "slides": slides,
                "status": "content_generated"
            }
        }
    )
    return {
    "status": "success",
    "slides": slides
}

@router.post("/{presentation_id}/generate-ppt")
def generate_ppt(presentation_id: str):

    presentation = presentations_collection.find_one(
        {"_id": ObjectId(presentation_id)}
    )

    if not presentation:
        return {"error": "Presentation not found"}

    filename = f"presentations/{presentation_id}.pptx"

    create_ppt(
        presentation["slides"],
        filename
    )

    presentations_collection.update_one(
        {"_id": ObjectId(presentation_id)},
        {
            "$set": {
                "ppt_file": filename,
                "status": "ppt_generated"
            }
        }
    )

    return {
        "status": "success",
        "file": filename
    }
from fastapi.responses import FileResponse

from fastapi.responses import FileResponse

@router.get("/{presentation_id}/download")
def download_ppt(presentation_id: str):

    presentation = presentations_collection.find_one(
        {"_id": ObjectId(presentation_id)}
    )

    if not presentation:
        return {"error": "Presentation not found"}

    return FileResponse(
        presentation["ppt_file"],
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        filename=f"{presentation_id}.pptx"
    )