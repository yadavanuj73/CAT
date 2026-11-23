"""
Full End-to-End API Integration Suite.
Tests every API route called by the frontend against the FastAPI application.
"""

import io
import uuid
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import init_db


@pytest.mark.asyncio
async def test_full_api_endpoint_integration():
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # 1. Health check
        res = await client.get("/api/health")
        assert res.status_code == 200
        assert res.json()["status"] == "healthy"

        # 2. Registration
        email = f"integ_{uuid.uuid4().hex[:8]}@cat2026.org"
        password = "SecurePassword123!"
        res = await client.post("/api/auth/register", json={
            "email": email,
            "password": password,
            "full_name": "Integration Tester"
        })
        assert res.status_code in [200, 201]
        reg_data = res.json()
        assert "access_token" in reg_data
        user_id = reg_data["user"]["id"]

        # 3. Login
        res = await client.post("/api/auth/login", json={
            "email": email,
            "password": password
        })
        assert res.status_code == 200
        token = res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 4. Auth Me
        res = await client.get("/api/auth/me", headers=headers)
        assert res.status_code == 200
        assert res.json()["email"] == email

        # 5. BYOK Session Key
        res = await client.post("/api/keys/session", headers=headers, json={
            "api_key": "sk-proj-test123456789012345678901234"
        })
        assert res.status_code == 200

        # 6. Key Status
        res = await client.get("/api/keys/status", headers=headers)
        assert res.status_code == 200
        status_data = res.json()
        assert status_data["is_set"] is True
        assert "sk-proj-test" not in status_data["masked_key"]

        # 7. Paper Listing
        res = await client.get("/api/papers", headers=headers)
        assert res.status_code == 200

        # 8. Questions Listing & Stats
        res = await client.get("/api/questions", headers=headers)
        assert res.status_code == 200
        res = await client.get("/api/questions/stats", headers=headers)
        assert res.status_code == 200

        # 9. Paper Analysis (QA, DILR, VARC)
        for sec in ["QA", "DILR", "VARC"]:
            res = await client.get(f"/api/analysis/{sec}?decay_factor=0.85", headers=headers)
            assert res.status_code == 200
            data = res.json()
            assert data["section"] == sec
            assert "difficulty_distribution" in data
            assert "top_topics" in data

        res = await client.post("/api/analysis/run", headers=headers, json={
            "section": "QA",
            "recency_decay_factor": 0.80
        })
        assert res.status_code == 200

        # 10. Predictions API
        res = await client.get("/api/predictions", headers=headers)
        assert res.status_code == 200
        pred_data = res.json()
        assert "predictions" in pred_data
        assert len(pred_data["predictions"]) > 0

        res = await client.post("/api/predictions/generate", headers=headers, json={
            "section": "QA",
            "target_year": 2026
        })
        assert res.status_code == 200

        # 11. Mock Exam Generation & Attempt Grading
        res = await client.post("/api/mocks/generate", headers=headers, json={
            "exam_type": "sectional",
            "section": "QA",
            "question_count": 5,
            "duration_minutes": 20
        })
        assert res.status_code == 201
        mock_data = res.json()
        mock_id = mock_data["id"]
        questions = mock_data["questions"]
        assert len(questions) >= 4

        # Attempt submission
        attempt_responses = {str(q["id"]): q["correct_answer"] for q in questions[:3]}
        res = await client.post(f"/api/mocks/{mock_id}/attempt", headers=headers, json={
            "responses": attempt_responses,
            "time_spent_seconds": 600
        })
        assert res.status_code == 200
        attempt_res = res.json()
        assert attempt_res["correct_count"] == 3
        assert attempt_res["total_score"] > 0

        # 12. Mock List & Get
        res = await client.get("/api/mocks", headers=headers)
        assert res.status_code == 200
        res = await client.get(f"/api/mocks/{mock_id}", headers=headers)
        assert res.status_code == 200

        # 13. Logout
        res = await client.post("/api/auth/logout", headers=headers)
        assert res.status_code == 200
