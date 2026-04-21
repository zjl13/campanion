from __future__ import annotations

from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.time import now_in_timezone
from app.models.engagement import ProofReview, ProofSubmission
from app.models.planning import Task
from app.models.user import User
from app.services.chat_service import create_message


def save_proof_file(filename: str, payload: bytes) -> str:
    target_dir = Path(settings.proof_storage_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / filename
    target_path.write_bytes(payload)
    return str(target_path.as_posix())


def evaluate_submission(task: Task, file_url: str | None, text_note: str | None) -> tuple[str, float, str]:
    normalized_note = (text_note or "").strip()
    proof_type = str(task.proof_requirement.get("type", "image_or_text"))
    if file_url:
        return "accepted", 0.82, "材料与任务记录方式匹配，已先为你记为完成。"
    if proof_type in {"text", "text_or_image", "image_or_text"} and len(normalized_note) >= 12:
        return "accepted", 0.74, "文字说明基本够用，已为你记录完成。"
    if normalized_note:
        return "needs_more_evidence", 0.43, "我看到你已经有进展了，再补一张图或多写一句会更稳。"
    return "rejected", 0.18, "当前材料信息太少，我还没法确认这次打卡。"


def submit_proof(
    db: Session,
    *,
    user: User,
    task: Task,
    filename: str | None,
    file_bytes: bytes | None,
    text_note: str | None,
) -> tuple[ProofSubmission, ProofReview]:
    now = now_in_timezone(user.timezone)
    file_url = None
    media_type = "text"
    if filename and file_bytes:
        file_url = save_proof_file(filename, file_bytes)
        media_type = "image"

    proof = ProofSubmission(
        task_id=task.id,
        user_id=user.id,
        media_type=media_type,
        file_url=file_url,
        text_note=text_note,
        submitted_at=now,
    )
    db.add(proof)
    db.flush()

    review_status, confidence, feedback = evaluate_submission(task, file_url, text_note)
    review = ProofReview(
        proof_id=proof.id,
        review_status=review_status,
        confidence=confidence,
        feedback=feedback,
        raw_model_output={
            "evidence_summary": "mock_review",
            "has_file": bool(file_url),
            "text_length": len((text_note or "").strip()),
        },
        reviewed_at=now,
    )
    db.add(review)

    if review_status == "accepted":
        task.status = "completed"
        if text_note:
            task.completion_note = text_note

    create_message(
        db,
        user_id=user.id,
        buddy_id=task.goal.buddy_id,
        role="assistant",
        content=feedback,
        message_type="checkin_feedback",
        related_goal_id=task.goal_id,
        related_task_id=task.id,
    )
    return proof, review


def get_review(db: Session, proof_id: str) -> tuple[ProofSubmission, ProofReview] | None:
    proof = db.scalar(select(ProofSubmission).where(ProofSubmission.id == proof_id))
    if not proof:
        return None
    review = db.scalar(select(ProofReview).where(ProofReview.proof_id == proof_id))
    if not review:
        return None
    return proof, review

