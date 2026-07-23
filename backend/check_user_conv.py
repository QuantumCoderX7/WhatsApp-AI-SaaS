import asyncio
import httpx

async def check():
    async with httpx.AsyncClient() as client:
        login = await client.post("http://localhost:8000/api/v1/auth/login", json={"email": "rayyanasim19@gmail.com", "password": "password123"})
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        convs = (await client.get("http://localhost:8000/api/v1/conversations", headers=headers)).json()
        print("=== ACTIVE CONVERSATIONS ===")
        for c in convs:
            print(f"ID: {c['id']} | Phone: {c['customer_phone']} | Name: {c['customer_name']} | Status: {c['status']}")

            msgs = (await client.get(f"http://localhost:8000/api/v1/conversations/{c['id']}/messages", headers=headers)).json()
            print(f"--- Messages ({len(msgs)}) ---")
            for m in msgs:
                print(f"[{m['sender_type']}] {m['content']}")

if __name__ == "__main__":
    asyncio.run(check())
