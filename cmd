gcloud functions deploy slack-x-chatgpt ^
--gen2 ^
--runtime=python39 ^
--region=asia-northeast1 ^
--source=. ^
--entry-point=handler ^
--trigger-http ^
--allow-unauthenticated ^

curl -X POST http://localhost:8080 -H 'Content-Type: application/json' -d '{"event": {"type": "app_mention", "text": "hello"}}' 

curl -X POST -H "Content-Type: application/json" -d "{\"event\":{\"type\":\"app_mention\", \"text\": \"hello\"}}" http://localhost:8080/
