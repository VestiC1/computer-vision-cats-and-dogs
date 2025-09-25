from config.settings import DB_CONFIG
from sqlalchemy import URL
from sqlmodel import Field, SQLModel, create_engine, Session
from datetime import datetime, timezone

# Chargement en memoire et modification des metadata de l'ORM
from .model import *

def get_utc_timestamp():
    return datetime.now(timezone.utc).replace(tzinfo=None)

# Création URL de connexion avec la fonction SQLAlchemy
POSTGRES_URL = URL.create(
    drivername="postgresql+psycopg2",
    username=DB_CONFIG["user"],
    password=DB_CONFIG["password"],
    host=DB_CONFIG["host"],
    port=DB_CONFIG["port"],
    database=DB_CONFIG["name"],
)

# Création du moteur de connexion
engine = create_engine(POSTGRES_URL, echo=True) # `echo=True` pour afficher les logs SQL

def create_tables():
    """Crée toutes les tables définies dans les modèles SQLModel."""
    global engine

    SQLModel.metadata.create_all(engine)

def drop_tables():
    global engine
    
    SQLModel.metadata.drop_all(engine)

def insert_feedback(id, value, prob_cat, prob_dog):
    global engine
    
    feedback = Feedback(id=id, feed_back_value=value, prob_cat=prob_cat, prob_dog=prob_dog, last_modified=get_utc_timestamp())

    with Session(engine) as conn:
        conn.add(feedback)
        conn.commit()

def insert_monitoring(time, succes):
    global engine

    monitoring = Monitoring(timestamp=get_utc_timestamp(), inference_time=time, succes=succes)

    with Session(engine) as conn:
        conn.add(monitoring)
        conn.commit()

def create_initial_feedback(prob_cat: float, prob_dog: float) -> Feedback:
    """Crée une entrée de feedback initiale (sans avis utilisateur)."""
    global engine
    feedback = Feedback(
        feed_back_value=0,  # 0 = pas de feedback
        prob_cat=prob_cat,
        prob_dog=prob_dog,
        last_modified=get_utc_timestamp(),
    )
    with Session(engine) as conn:
        conn.add(feedback)
        conn.commit()
        conn.refresh(feedback)
        return feedback

def update_feedback(feedback_id: int, feedback_value: int):
    """Met à jour le feedback utilisateur (1=Oui, 2=Non)."""
    global engine
    with Session(engine) as conn:
        feedback = conn.get(Feedback, feedback_id)
        if feedback:
            feedback.feed_back_value = feedback_value
            feedback.last_modified = get_utc_timestamp()
            conn.commit()
            return feedback
    return None 


if __name__ == "__main__":
    create_tables()
    #insert_feedback(1, 2, 0.7, 0.3)
    #insert_monitoring(1, 2.5, True)
    pass