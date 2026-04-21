from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.serializers import serialize_review
from app.db.session import get_db
from app.models.user import User
from app.schemas.proof import ProofReviewResponse
from app.services.proof_review import get_review


router = APIRouter(prefix="/proofs", tags=["proofs"])


@router.get("/{proof_id}", response_model=ProofReviewResponse)
def get_proof_review(
    proof_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProofReviewResponse:
    result = get_review(db, proof_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proof not found")
    proof, review = result
    if proof.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proof not found")
    return ProofReviewResponse.model_validate(serialize_review(proof.id, review))

