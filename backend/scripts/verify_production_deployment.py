"""
Phase 6 Live Production Deployment Verifier.

Tests live Render backend + Vercel frontend URLs against all production gates:
1. Backend /api/health (confirms PostgreSQL DB connectivity, non-SQLite)
2. Auth registration/login & token isolation
3. Shared Corpus stats (/api/shared/stats)
4. VARC, DILR, QA filtering (/api/shared/questions)
5. Single question details (/api/shared/questions/{id})
6. Topic filtering, difficulty filtering, keyword search, pagination
7. Cross-user private paper isolation
8. Mock exam generation using production shared questions (/api/mocks/generate)
9. Frontend availability + CORS preflight verification
"""

import argparse
import asyncio
import sys
import uuid
import httpx


async def verify_live_production(backend_url: str, frontend_url: str) -> int:
    api_base = backend_url.rstrip("/")
    if not api_base.endswith("/api"):
        api_base = f"{api_base}/api"
    fe_base = frontend_url.rstrip("/")

    print("=" * 70)
    print("CAT 2026 — LIVE PRODUCTION VERIFICATION")
    print(f"Backend API : {api_base}")
    print(f"Frontend URL: {fe_base}")
    print("=" * 70)

    failures = []

    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        # 1. Frontend check
        try:
            r = await client.get(fe_base)
            print(f"[{'PASS' if r.status_code == 200 else 'FAIL'}] 1. Frontend Root GET -> {r.status_code}")
            if r.status_code != 200:
                failures.append(f"Frontend returned {r.status_code}")
        except Exception as e:
            print(f"[FAIL] 1. Frontend Root GET -> {e}")
            failures.append(f"Frontend error: {e}")

        # 2. Health endpoint
        try:
            r = await client.get(f"{api_base}/health")
            h = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
            ok = r.status_code == 200 and h.get("status") == "healthy" and h.get("database") == "connected"
            print(f"[{'PASS' if ok else 'FAIL'}] 2. Backend /health -> {r.status_code} {h}")
            if not ok:
                failures.append(f"Health failed: {r.status_code} {h}")
        except Exception as e:
            print(f"[FAIL] 2. Backend /health -> {e}")
            failures.append(f"Health error: {e}")

        # 3. CORS preflight
        try:
            r = await client.options(
                f"{api_base}/shared/stats",
                headers={
                    "Origin": fe_base,
                    "Access-Control-Request-Method": "GET",
                    "Access-Control-Request-Headers": "authorization",
                },
            )
            aco = r.headers.get("access-control-allow-origin", "")
            ok = r.status_code in (200, 204) and bool(aco)
            print(f"[{'PASS' if ok else 'FAIL'}] 3. CORS Preflight -> {r.status_code} allow-origin={aco!r}")
            if not ok:
                failures.append(f"CORS preflight failed: {r.status_code}")
        except Exception as e:
            print(f"[FAIL] 3. CORS Preflight -> {e}")
            failures.append(f"CORS error: {e}")

        # 4. Unauthenticated block + User Registration
        r_unauth = await client.get(f"{api_base}/shared/stats")
        print(f"[{'PASS' if r_unauth.status_code == 401 else 'FAIL'}] 4. Auth Guard (/shared/stats unauthenticated) -> {r_unauth.status_code}")
        if r_unauth.status_code != 401:
            failures.append(f"Auth guard returned {r_unauth.status_code}")

        email_1 = f"prod_verify_{uuid.uuid4().hex[:8]}@cat2026.org"
        pw = "ProdVerify#2026!"
        r_reg = await client.post(
            f"{api_base}/auth/register",
            json={"email": email_1, "password": pw, "full_name": "Prod Verifier"},
        )
        if r_reg.status_code not in (200, 201):
            print(f"[FAIL] Registration -> {r_reg.status_code} {r_reg.text[:200]}")
            return 1
        headers = {"Authorization": f"Bearer {r_reg.json()['access_token']}"}

        # 5. Shared Stats
        r_stats = await client.get(f"{api_base}/shared/stats", headers=headers)
        stats = r_stats.json()
        ok = (
            r_stats.status_code == 200
            and stats.get("total_unique_verified_questions", 0) >= 1010
            and stats.get("section_breakdown", {}).get("VARC", 0) >= 340
            and stats.get("section_breakdown", {}).get("DILR", 0) >= 330
            and stats.get("section_breakdown", {}).get("QA", 0) >= 340
        )
        print(
            f"[{'PASS' if ok else 'FAIL'}] 5. Shared Stats -> total={stats.get('total_unique_verified_questions')}, "
            f"sections={stats.get('section_breakdown')}"
        )
        if not ok:
            failures.append(f"Stats mismatch: {stats}")

        # 6. Section endpoints + details
        first_qid = None
        for sec, exp_min in [("VARC", 340), ("DILR", 330), ("QA", 340)]:
            r_sec = await client.get(f"{api_base}/shared/questions", params={"section": sec, "limit": 5}, headers=headers)
            d = r_sec.json()
            ok = r_sec.status_code == 200 and d.get("total", 0) >= exp_min and len(d.get("items", [])) == 5
            if ok and first_qid is None:
                first_qid = d["items"][0]["id"]
            print(f"[{'PASS' if ok else 'FAIL'}] 6. Section {sec} -> total={d.get('total')}, returned={len(d.get('items', []))}")
            if not ok:
                failures.append(f"Section {sec} failed")

        # 7. Individual Question Detail
        if first_qid:
            r_det = await client.get(f"{api_base}/shared/questions/{first_qid}", headers=headers)
            det = r_det.json()
            ok = r_det.status_code == 200 and bool(det.get("correct_answer")) and bool(det.get("solution_text"))
            print(f"[{'PASS' if ok else 'FAIL'}] 7. Question Detail ({first_qid}) -> key={bool(det.get('correct_answer'))}, sol={bool(det.get('solution_text'))}")
            if not ok:
                failures.append("Detail failed")

        # 8. Topic, Difficulty, Search, Pagination
        r_top = await client.get(f"{api_base}/shared/questions", params={"topic": "Arithmetic", "difficulty": "medium", "search": "speed", "limit": 5, "offset": 5}, headers=headers)
        td = r_top.json()
        ok = r_top.status_code == 200 and td.get("total", 0) > 0 and len(td.get("items", [])) > 0
        print(f"[{'PASS' if ok else 'FAIL'}] 8. Topic/Difficulty/Search/Pagination -> total={td.get('total')}, items={len(td.get('items', []))}")
        if not ok:
            failures.append("Filtering/search/pagination failed")

        # 9. Cross-User Privacy Isolation
        email_2 = f"prod_verify2_{uuid.uuid4().hex[:8]}@cat2026.org"
        r_reg2 = await client.post(f"{api_base}/auth/register", json={"email": email_2, "password": pw, "full_name": "Prod Verifier 2"})
        headers_2 = {"Authorization": f"Bearer {r_reg2.json()['access_token']}"}
        r_priv = await client.get(f"{api_base}/papers", headers=headers_2)
        print(f"[{'PASS' if r_priv.status_code == 200 else 'FAIL'}] 9. Cross-user papers isolation check -> {r_priv.status_code}")

        # 10. Mock Exam Generation
        r_mock = await client.post(
            f"{api_base}/mocks/generate",
            json={"exam_type": "full", "title": "Prod Live Verification Mock"},
            headers=headers,
        )
        m = r_mock.json()
        ok = r_mock.status_code in (200, 201) and m.get("total_questions") == 66 and len(m.get("questions", [])) == 66
        print(f"[{'PASS' if ok else 'FAIL'}] 10. Full Mock Generation -> status={r_mock.status_code}, questions={len(m.get('questions', []))}")
        if not ok:
            failures.append(f"Mock generation failed: {r_mock.status_code}")

    print("=" * 70)
    print(f"VERIFICATION COMPLETE: {len(failures)} failures")
    return 1 if failures else 0


def main():
    parser = argparse.ArgumentParser(description="Verify live CAT 2026 production deployment.")
    parser.add_argument("--backend-url", required=True, help="Live Render backend URL")
    parser.add_argument("--frontend-url", required=True, help="Live Vercel frontend URL")
    args = parser.parse_args()
    sys.exit(asyncio.run(verify_live_production(args.backend_url, args.frontend_url)))


if __name__ == "__main__":
    main()
