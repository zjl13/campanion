def test_goal_planning_flow(client, auth_headers):
    pref_response = client.put(
        "/api/v1/me/preferences",
        headers=auth_headers,
        json={
            "preferred_focus_blocks": [{"weekday": 2, "start": "19:00", "end": "21:00"}],
            "timezone": "Asia/Shanghai",
        },
    )
    assert pref_response.status_code == 200

    buddy_response = client.post(
        "/api/v1/buddies",
        headers=auth_headers,
        json={
            "style": "gentle",
            "tone": "supportive",
            "strictness": "standard",
            "buddy_type": "study",
            "language": "zh-CN",
        },
    )
    assert buddy_response.status_code == 200
    buddy_id = buddy_response.json()["buddy_id"]

    block_response = client.post(
        "/api/v1/calendar/blocks",
        headers=auth_headers,
        json={
            "title": "高数课",
            "type": "class",
            "weekday": 2,
            "start_time": "20:00:00",
            "end_time": "21:30:00",
            "repeat": "weekly",
        },
    )
    assert block_response.status_code == 200

    goal_response = client.post(
        "/api/v1/goals",
        headers=auth_headers,
        json={
            "title": "英语四级复习",
            "description": "词汇、阅读、听力",
            "goal_type": "study",
            "deadline": "2026-06-15T23:59:59+08:00",
            "priority": "high",
            "buddy_id": buddy_id,
        },
    )
    assert goal_response.status_code == 200
    goal_id = goal_response.json()["goal_id"]

    plan_response = client.get(f"/api/v1/goals/{goal_id}/plan", headers=auth_headers)
    assert plan_response.status_code == 200
    plan_payload = plan_response.json()
    assert len(plan_payload["tasks"]) >= 7
    assert "risk_score" in plan_payload

    today_response = client.get("/api/v1/tasks/today", headers=auth_headers)
    assert today_response.status_code == 200

    risk_response = client.get(f"/api/v1/goals/{goal_id}/risk", headers=auth_headers)
    assert risk_response.status_code == 200
    assert risk_response.json()["risk_level"] in {"low", "medium", "high"}


def test_reschedule_chat_and_proof_flow(client, auth_headers):
    goal_response = client.post(
        "/api/v1/goals",
        headers=auth_headers,
        json={
            "title": "30 天读完一本书",
            "description": "每天阅读和整理",
            "goal_type": "reading",
            "deadline": "2026-05-20T23:59:59+08:00",
            "priority": "medium",
        },
    )
    goal_id = goal_response.json()["goal_id"]
    plan_response = client.get(f"/api/v1/goals/{goal_id}/plan", headers=auth_headers)
    first_task = plan_response.json()["tasks"][0]

    chat_response = client.post(
        "/api/v1/chat/messages",
        headers=auth_headers,
        json={"message": "我今晚不太想做了", "context_task_id": first_task["id"]},
    )
    assert chat_response.status_code == 200
    assert chat_response.json()["actions"]

    reschedule_response = client.post(
        f"/api/v1/tasks/{first_task['id']}/reschedule",
        headers=auth_headers,
        json={"reason_text": "今晚临时有组会，原来的时间做不了", "preferred_strategy": "auto"},
    )
    assert reschedule_response.status_code == 200
    new_task_id = reschedule_response.json()["new_task"]["id"]

    proof_response = client.post(
        f"/api/v1/tasks/{new_task_id}/proofs",
        headers=auth_headers,
        files={"file": ("reading.png", b"fake-image-bytes", "image/png")},
        data={"text_note": "今天读完了两节并写了摘要"},
    )
    assert proof_response.status_code == 200
    proof_id = proof_response.json()["proof_id"]

    review_response = client.get(f"/api/v1/proofs/{proof_id}", headers=auth_headers)
    assert review_response.status_code == 200
    assert review_response.json()["review_status"] in {"accepted", "needs_more_evidence", "rejected"}

    stats_response = client.get("/api/v1/stats/overview", headers=auth_headers)
    assert stats_response.status_code == 200
    assert "completed_tasks" in stats_response.json()
