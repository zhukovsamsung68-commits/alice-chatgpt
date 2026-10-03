import os

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from openai import OpenAI

app = FastAPI()

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    timeout=3.2,
    max_retries=0
)


@app.get("/")
def home():
    return {
        "status": "ok",
        "service": "alice-chatgpt"
    }


@app.post("/")
async def alice_webhook(request: Request):
    try:
        data = await request.json()

        alice_request = data.get("request") or {}

        user_text = alice_request.get(
            "original_utterance",
            ""
        ).strip()

        if not user_text:
            return alice_response("Я вас слушаю.")

        if user_text.lower() == "ping":
            return alice_response("pong")

        response = client.responses.create(
            model="gpt-5.4-mini",
            input=user_text
        )

        answer = response.output_text.strip()

        if not answer:
            return alice_response(
                "Не удалось получить ответ."
            )

        return alice_response(answer)

    except Exception as e:
        print("ERROR:", repr(e))

        return alice_response(
            "Не успел получить ответ. Попробуйте ещё раз."
        )


def alice_response(text):
    return JSONResponse(
        content={
            "version": "1.0",
            "response": {
                "text": text[:1024],
                "end_session": False
            }
        }
    )
