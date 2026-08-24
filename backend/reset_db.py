from app.database.connection import engine, Base
from app.models.base import Candidate, Resume, Job, MatchResult, MatchEvidence

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
print("Database successfully wiped and reset to clean state!")
