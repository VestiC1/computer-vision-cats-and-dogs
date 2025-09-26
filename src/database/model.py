from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime
from typing import Optional

class Feedback(SQLModel, table=True):
    id: int = Field(primary_key=True)
    feed_back_value: int
    prob_cat: float
    prob_dog: float
    last_modified: datetime

    # Relation optionnelle (pour accéder aux monitorings depuis un feedback)
    monitorings: list["Monitoring"] = Relationship(back_populates="feedback")

class Monitoring(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    feedback_id: int = Field(foreign_key="feedback.id")  # feedback_id est la clé étrangère qui lie Monitoring à Feedback.
    timestamp: datetime
    inference_time: float
    succes: bool

    # Relation optionnelle (pour accéder au feedback depuis un monitoring)
    feedback: Optional["Feedback"] = Relationship(back_populates="monitorings")
