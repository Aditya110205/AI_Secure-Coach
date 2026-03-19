# Secure AI Coach Chat System

A production-ready AI coaching platform where every conversation is fully encrypted and accessible only with explicit user consent. Built with security-first principles — even developers with direct database access cannot read chat content.

---

## Architecture Overview
```
User → FastAPI → Gemini AI → Fernet Encrypt → MySQL
                                    ↑
                            Key derived from
                            user password (SHA-256)
```

**Stack:** Next.js · FastAPI · MySQL · Fernet (AES-128) · Gemini 2.0 Flash · Docker

---

## Security Approach

All chat data is encrypted using Fernet symmetric encryption (AES-128-CBC + HMAC-SHA256) before it ever touches the database. The encryption key is derived from the user's password using SHA-256, meaning the key never exists independently — it is mathematically bound to something only the user knows.

Passwords are stored as SHA-256 hashes only. Plain text passwords are never persisted anywhere in the system.

Access to chat history requires an explicit consent flag on every request. Without `consent=true`, the API returns an error and no data is returned — modeling informed, active consent rather than passive access.

Every message in the database appears as an unreadable encrypted blob such as `gAAAAABl9x2K...`. Without the user's key, the data is meaningless to anyone who accesses the database directly.

---

## Key Design Decisions

**Why Fernet?**
Fernet is built on AES-128-CBC combined with HMAC-SHA256 for authentication. It is authenticated encryption, meaning it detects any tampering with the stored data. It is simple, battle-tested, and requires no external infrastructure beyond the `cryptography` Python package.

**Why derive the key from the user's password?**
The encryption key never exists as a standalone secret. It is derived on-the-fly from the user's password each time it is needed. This means database administrators, backend developers, and cloud infrastructure teams cannot decrypt conversations without knowing the user's actual password.

**Why a consent flag instead of just authentication?**
Authentication proves who you are. Consent proves you actively want to share your data. The `/chats` endpoint requires `consent=true` as a deliberate parameter on every call, forcing the client to surface an explicit user action rather than silently fetching sensitive data in the background.

**Why store mood scores separately from chat content?**
Mood scores are integers between 1 and 10. Keeping them unencrypted alongside the encrypted chat blobs allows the system to generate trend analytics and dashboards without ever needing to decrypt the actual conversation content. Privacy is preserved while still enabling useful insights.

---

## Impressive Features

**Mood Tracker**
Every message sent by the user is analyzed by Gemini and assigned an emotional tone score from 1 (very distressed) to 10 (very positive). These scores are stored per message and exposed through the `/mood-trend` endpoint, allowing users to visualize their mental health progress over time without exposing the underlying conversations.

**Session Memory**
The last five conversations are fetched and passed as context to Gemini on every new message. The AI coach remembers what was discussed earlier in the session, making interactions feel continuous and personal rather than stateless and repetitive.

---

## API Endpoints

`GET /` — Health check, confirms the backend is running.

`GET /create-user` — Creates a test user with a derived encryption key. Returns the user ID.

`POST /chat?user_id=1&message=...` — Accepts a user message, fetches session history, calls Gemini, encrypts the exchange, saves to MySQL, and returns the AI response.

`GET /chats?user_id=1&consent=true` — Fetches all encrypted chat rows for the user, decrypts them using the user's key, and returns the full conversation history with timestamps and mood scores.

`GET /mood-trend?user_id=1&consent=true` — Returns a chronological list of mood scores without decrypting any chat content.

---

## Setup Instructions

**Option A — Docker (recommended)**
```bash
git clone https://github.com/Aditya110205/AI_Secure-Coach.git
cd AI_Secure-Coach

echo "GEMINI_API_KEY=your_key_here" > .env

docker-compose up --build

curl http://localhost:8000/create-user
curl -X POST "http://localhost:8000/chat?user_id=1&message=I feel stressed"
curl "http://localhost:8000/chats?user_id=1&consent=true"
```

**Option B — Local without Docker**
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Configure your MySQL connection in .env
uvicorn app.main:app --reload
```

---

## Scalability to 100,000 Users

The current architecture is designed for correctness and security. Scaling it to 100,000 active users would require the following changes.

Database connections would need pooling configuration in SQLAlchemy with `pool_size=20` and `max_overflow=40` to handle concurrent requests without exhausting MySQL connections.

Encryption key derivation is synchronous and CPU-bound. At scale this should move to an async worker queue using Celery and Redis so that encryption does not block the API thread pool.

Gemini API calls are subject to rate limits. A request queue with exponential backoff, combined with multiple API keys rotating in round-robin, would prevent request failures under load.

Encrypted chat blobs should migrate from MySQL TEXT columns to AWS S3 with server-side encryption (SSE-KMS). MySQL would retain only metadata — user IDs, timestamps, mood scores — keeping the database lean and fast.

The test user system should be replaced with JWT-based authentication including refresh tokens, proper password hashing using bcrypt, and session expiry.

At infrastructure level, containerized services behind a load balancer with Kubernetes horizontal pod autoscaling would handle traffic spikes automatically.

---

## Future Scope

**Security**
The most significant security upgrade would be moving to a zero-knowledge architecture where the server never sees the encryption key at all. The key would be derived entirely on the client side, and only ciphertext would ever be transmitted. Combined with end-to-end encryption at the frontend layer, this would make the system provably private even in the event of a full server compromise.

A blockchain-based audit log would provide an immutable, tamper-proof record of every data access event. Users would be able to independently verify who accessed their data and when, without trusting the platform's own logs.

Homomorphic encryption would allow mood scoring and analytics to run directly on encrypted data, eliminating the current trade-off between analytics capability and content privacy.

Hardware Security Modules such as AWS CloudHSM would replace software-based key storage, providing tamper-resistant hardware protection for master keys.

**AI and Coaching**
Voice input via Whisper API transcription would allow users to speak naturally rather than type, making the coaching experience more accessible and human. The coach could respond with both text and synthesized audio.

Crisis detection would monitor for sustained low mood scores and automatically route the user toward professional support resources or a human coach, adding a meaningful safety net for vulnerable users.

Personalized coaching style would evolve the AI's tone and approach based on weeks of mood history — becoming more direct with users who respond well to challenge, and more gentle with those who need encouragement.

Goal tracking would allow users to set specific objectives at the start of a session and have the AI check in on progress across subsequent conversations, creating continuity between sessions.

**Infrastructure**
WebSocket support would replace the current request-response model with real-time streaming responses, making the chat feel instant and live rather than transactional.

A Redis caching layer would store the last five messages per user in memory, eliminating the database read that currently happens on every single chat request.

HIPAA compliance measures including formal audit logging, configurable data retention policies, and Business Associate Agreements with cloud providers would make the platform viable for healthcare and enterprise customers.

**Frontend**
The Next.js frontend would include a mood dashboard with an interactive 30-day trend chart, a WhatsApp-style chat interface with message bubbles, a consent management screen where users can grant or revoke data access at any time, and an option to export the full chat history as an encrypted ZIP file.

---

## Time Spent

Approximately 8 to 10 hours, covering backend architecture and encryption design, FastAPI endpoint development, database modelling, Gemini integration with session memory, mood tracking feature, Docker configuration, and documentation.
