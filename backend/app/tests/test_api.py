def test_health(client):
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_upload_and_chat(client):
    r = client.post(
        "/api/v1/documents",
        files={
            "file": (
                "kb.txt",
                "RAG 是检索增强生成，先检索后生成。".encode("utf-8"),
                "text/plain",
            )
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["chunks"] >= 1

    r2 = client.post("/api/v1/chat", json={"question": "什么是 RAG？"})
    assert r2.status_code == 200
    # SSE body must carry the event types
    assert "sources" in r2.text
    assert "token" in r2.text
