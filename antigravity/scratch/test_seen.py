
import asyncio
from utils.send_messenger import send_messenger_action

async def test_seen():
    uid = "MESSENGER_USER_ID"
    print(f"Sending mark_seen to {uid}...")
    await send_messenger_action(uid, "mark_seen")
    print("Done.")

if __name__ == "__main__":
    asyncio.run(test_seen())
