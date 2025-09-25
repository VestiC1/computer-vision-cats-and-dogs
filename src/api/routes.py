from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import sys
from pathlib import Path
import time

# Ajouter le répertoire racine au path
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from .auth import verify_token
from src.models.predictor import CatDogPredictor
from src.monitoring.metrics import time_inference
from src.database.crud import create_initial_feedback, update_feedback

# Configuration des templates
TEMPLATES_DIR = ROOT_DIR / "src" / "web" / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

router = APIRouter()

# Initialisation du prédicteur
predictor = CatDogPredictor()

@router.get("/", response_class=HTMLResponse)
async def welcome(request: Request):
    """Page d'accueil avec interface web"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "model_loaded": predictor.is_loaded()
    })

@router.get("/info", response_class=HTMLResponse)
async def info_page(request: Request):
    """Page d'informations"""
    model_info = {
        "name": "Cats vs Dogs Classifier",
        "version": "1.0.0",
        "description": "Modèle CNN pour classification chats/chiens",
        "parameters": predictor.model.count_params() if predictor.is_loaded() else 0,
        "classes": ["Cat", "Dog"],
        "input_size": f"{predictor.image_size[0]}x{predictor.image_size[1]}",
        "model_loaded": predictor.is_loaded()
    }
    return templates.TemplateResponse("info.html", {
        "request": request, 
        "model_info": model_info
    })

@router.get("/inference", response_class=HTMLResponse)
async def inference_page(request: Request):
    """Page d'inférence"""
    return templates.TemplateResponse("inference.html", {
        "request": request,
        "model_loaded": predictor.is_loaded()
    })

@router.post("/api/predict")
@time_inference
async def predict_api(
    file: UploadFile = File(...),
    token: str = Depends(verify_token)
):
    if not predictor.is_loaded():
        raise HTTPException(status_code=503, detail="Modèle non disponible")

    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Format d'image invalide")

    try:
        image_data = await file.read()
        result = predictor.predict(image_data)

        # Crée un feedback initial dans la base
        feedback = create_initial_feedback(
            prob_cat=result['probabilities']['cat'],
            prob_dog=result['probabilities']['dog'],
        )

        response_data = {
            "filename": file.filename,
            "prediction": result["prediction"],
            "confidence": f"{result['confidence']:.2%}",
            "probabilities": {
                "cat": result['probabilities']['cat'],
                "dog": result['probabilities']['dog'],
            },
            "feedback_id": feedback.id,  # Retourne l'ID du feedback pour la mise à jour
        }
        return response_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de prédiction: {str(e)}")

@router.post("/api/feedback")
async def save_feedback(request: Request):
    """Met à jour le feedback utilisateur."""
    data = await request.json()
    feedback_id = data.get('feedback_id')
    feedback_value = data.get('feedback_value')

    if not feedback_id or feedback_value not in [1, 2]:
        raise HTTPException(status_code=400, detail="Données invalides")

    try:
        feedback = update_feedback(feedback_id, feedback_value)
        if not feedback:
            raise HTTPException(status_code=404, detail="Feedback non trouvé")
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/info")
async def api_info():
    """Informations API JSON"""
    return {
        "model_loaded": predictor.is_loaded(),
        "model_path": str(predictor.model_path),
        "version": "1.0.0",
        "parameters": predictor.model.count_params() if predictor.is_loaded() else 0
    }

@router.get("/health")
async def health_check():
    """Vérification de l'état de l'API"""
    return {
        "status": "healthy",
        "model_loaded": predictor.is_loaded()
    }