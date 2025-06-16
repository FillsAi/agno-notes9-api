# Complete Beginner's Guide - Part 2: Database Tables and API Endpoints

## Part 3: Deep Dive into Each Component

### 3.1 Database Tables Explained

Our database automatically creates tables as needed. Here are the main table types:

#### **Agent Session Tables**

**Purpose**: Store conversation history for each AI agent

**Example Table**: `sage_sessions` (created by `agents/sage.py`)

**Structure**: 
```sql
CREATE TABLE sage_sessions (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255),           -- Who is chatting
    session_id VARCHAR(255),        -- Chat session identifier  
    agent_id VARCHAR(255),          -- Which agent (sage, scholar, etc.)
    message TEXT,                   -- User's message
    response TEXT,                  -- Agent's response
    model_id VARCHAR(255),          -- AI model used (amazon.nova-lite-v1:0)
    created_at TIMESTAMP,           -- When message was sent
    updated_at TIMESTAMP,           -- Last modification
    metadata JSONB                  -- Extra information
);
```

**Example data**:
```sql
-- Row 1: User starts conversation
INSERT INTO sage_sessions VALUES (
    1,                              -- id
    'user123',                      -- user_id  
    'sess_456',                     -- session_id
    'sage',                         -- agent_id
    'Hi, how can I check my order status?',  -- message
    'Hi! To check your order status online, you can...',  -- response
    'amazon.nova-lite-v1:0',        -- model_id
    '2024-01-15 10:30:00',          -- created_at
    '2024-01-15 10:30:00',          -- updated_at
    '{"tools_used": ["knowledge_search"], "response_time": 2.3}'  -- metadata
);

-- Row 2: User follows up
INSERT INTO sage_sessions VALUES (
    2,
    'user123',
    'sess_456', 
    'sage',
    'What if I lost my order number?',
    'No problem! You can find your order number by...',
    'amazon.nova-lite-v1:0',
    '2024-01-15 10:31:15',
    '2024-01-15 10:31:15',
    '{"tools_used": ["web_search"], "response_time": 3.1}'
);
```

**Code that uses it**: `agents/sage.py` line 67
```python
storage=PostgresAgentStorage(table_name="sage_sessions", db_url=db_url),
```

#### **Knowledge Base Table**

**Example Table**: `sage_knowledge` (vector storage)

**Purpose**: Store documents and information that the AI can search through

**Structure**:
```sql
CREATE TABLE sage_knowledge (
    id SERIAL PRIMARY KEY,
    content TEXT,                   -- Original text content
    embedding VECTOR(1536),        -- Vector representation (1536 numbers)
    document_name VARCHAR(255),     -- Source document
    chunk_index INTEGER,           -- Which part of document
    created_at TIMESTAMP,
    metadata JSONB                 -- Document information
);
```

**Example data**:
```sql
INSERT INTO sage_knowledge VALUES (
    1,
    'Our return policy allows returns within 30 days of purchase. Items must be in original condition with receipt.',
    '[0.23,0.87,0.12,0.45,...]',   -- 1536-dimensional vector
    'company_policies.pdf',
    1,
    '2024-01-15 09:00:00',
    '{"section": "Returns", "page": 5, "policy_type": "customer_service"}'
);
```

**Code that uses it**: `agents/sage.py` lines 84-86
```python
knowledge=AgentKnowledge(
    vector_db=PgVector(table_name="sage_knowledge", db_url=db_url, search_type=SearchType.hybrid)
),
```

#### **Team Storage Tables**

**Example Table**: `finance_researcher_team` (for team of agents)

**Purpose**: Store conversations when multiple agents work together

**Code location**: `teams/finance_researcher.py` lines 101-109
```python
storage=PostgresStorage(
    table_name="finance_researcher_team",
    db_url=db_url,
    mode="team",
    auto_upgrade_schema=True,
),
```

**Structure** (similar to agent sessions but includes team coordination):
```sql
CREATE TABLE finance_researcher_team (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255),
    session_id VARCHAR(255),
    team_id VARCHAR(255),           -- Which team handled this
    member_responses JSONB,         -- Individual agent responses
    final_response TEXT,            -- Coordinated team response
    created_at TIMESTAMP,
    metadata JSONB
);
```

#### **Workflow Storage Tables**

**Example Table**: `blog_post_generator_workflows`

**Purpose**: Store multi-step workflow progress

**Code location**: `workflows/blog_post_generator.py` lines 343-351
```python
storage=PostgresStorage(
    table_name="blog_post_generator_workflows",
    db_url=db_url,
    auto_upgrade_schema=True,
),
```

### 3.2 API Endpoints Explained

Our API follows REST patterns. Here are the main endpoints:

#### **Chat Endpoint**: `POST /v1/agents/{agent_id}/runs`

**Purpose**: Send a message to an AI agent and get a response

**File location**: `api/routes/agents.py` lines 68-103

**Input format**:
```json
{
  "message": "What is machine learning?",
  "stream": false,
  "model": "amazon.nova-lite-v1:0",
  "user_id": "user123",
  "session_id": "sess_456"
}
```

**Processing** (line-by-line explanation):
```python
@agents_router.post("/{agent_id}/runs", status_code=status.HTTP_200_OK)
async def run_agent(agent_id: AgentType, body: RunRequest):
    # Line 1: Log the incoming request for debugging
    logger.debug(f"RunRequest: {body}")

    # Lines 2-6: Create the appropriate agent based on agent_id
    try:
        agent: Agent = get_agent(
            model_id=body.model.value,      # Which AI model to use
            agent_id=agent_id,              # sage, scholar, etc.
            user_id=body.user_id,           # Track user across sessions
            session_id=body.session_id,     # Group related messages
        )
    except Exception as e:
        # If agent creation fails, return error
        raise HTTPException(status_code=404, detail=f"Agent not found: {str(e)}")

    # Lines 7-12: Handle streaming vs non-streaming responses
    if body.stream:
        # For real-time responses (text appears as it's generated)
        return StreamingResponse(
            chat_response_streamer(agent, body.message),
            media_type="text/event-stream",
        )
    else:
        # For complete responses (wait for full answer)
        response = agent.run(body.message, stream=False)
        return {"content": response.content if response.content else "No response generated"}
```

**Database interactions during this call**:
1. **Read**: Load conversation history from `{agent_id}_sessions` table
2. **Read**: Search knowledge base in `{agent_id}_knowledge` table  
3. **Write**: Save new message and response to `{agent_id}_sessions` table

**Output format**:
```json
{
  "content": "Machine learning is a branch of artificial intelligence (AI) that enables computers to learn and improve from experience without being explicitly programmed. Here's a simple breakdown:\n\n**How it works:**\n1. **Data Input**: Feed the computer lots of examples\n2. **Pattern Recognition**: Computer finds patterns in the data\n3. **Prediction**: Uses patterns to make predictions on new data\n\n**Real-world examples:**\n- Email spam detection\n- Netflix movie recommendations  \n- Voice assistants like Siri\n- Self-driving cars\n\n**Types:**\n- **Supervised Learning**: Learning from examples with known answers\n- **Unsupervised Learning**: Finding hidden patterns in data\n- **Reinforcement Learning**: Learning through trial and error\n\nThink of it like teaching a child to recognize cats - show them thousands of cat pictures, and eventually they'll be able to identify cats in new pictures!"
}
```

**Error handling**:
```python
# What can go wrong and how it's handled:

# 1. Invalid agent_id
if agent_id not in ["sage", "scholar"]:
    return HTTPException(404, "Agent not found")

# 2. Database connection failure  
if database_unreachable:
    return HTTPException(500, "Service temporarily unavailable")

# 3. AI model failure
if ai_model_error:
    return HTTPException(503, "AI service unavailable")
```

#### **Health Check Endpoint**: `GET /v1/health`

**Purpose**: Check if the API is working

**File location**: `api/routes/status.py` lines 11-21

**Code**:
```python
@status_router.get("/health")
def get_health():
    """Check the health of the Api"""
    return {
        "status": "success",
        "router": "status", 
        "path": "/health",
        "utc": current_utc_str(),
    }
```

**Example response**:
```json
{
  "status": "success",
  "router": "status",
  "path": "/health", 
  "utc": "2024-01-15T10:30:00.000Z"
}
```

**Use cases**:
- Load balancer checks if server is alive
- Monitoring systems verify API health
- Debugging connectivity issues

#### **List Agents Endpoint**: `GET /v1/agents`

**Purpose**: Show all available AI agents

**File location**: `api/routes/agents.py` lines 25-31

**Code**:
```python
@agents_router.get("", response_model=List[str])
async def list_agents():
    """Returns a list of all available agent IDs."""
    return get_available_agents()
```

**Example response**:
```json
["sage", "scholar", "test_sage"]
```

### 3.3 Configuration Files

#### **Database Configuration**: `db/settings.py`

**Purpose**: Configure how the application connects to the database

**Each setting explained**:
```python
class DbSettings(BaseSettings):
    # Database server location
    db_host: Optional[str] = None          # Example: "localhost" or "rds-endpoint.amazonaws.com"
    
    # Database server port
    db_port: Optional[int] = None          # Example: 5432 (standard PostgreSQL port)
    
    # Login credentials
    db_user: Optional[str] = None          # Example: "ai" (development) or "agno" (production)
    db_pass: Optional[str] = None          # Example: "ai" (development) or "agno9999!!" (production)
    
    # Database name
    db_database: Optional[str] = None      # Example: "ai"
    
    # Database driver (software that talks to database)
    db_driver: str = "postgresql+psycopg"  # PostgreSQL with psycopg driver
    
    # Automatically run database migrations on startup
    migrate_db: bool = False               # True = update database schema automatically
```

**Example values for development**:
```python
db_host = "localhost"           # Database runs on same computer
db_port = 5432                  # Standard PostgreSQL port
db_user = "ai"                  # Simple username
db_pass = "ai"                  # Simple password  
db_database = "ai"              # Database name
migrate_db = True               # Auto-update database structure
```

**Example values for production**:
```python
db_host = "agent-api-prd-db.c8vkj2k3h4l5.us-east-1.rds.amazonaws.com"  # RDS endpoint
db_port = 5432
db_user = "agno"                # More secure username
db_pass = "agno9999!!"          # Complex password
db_database = "ai"
migrate_db = True
```

**What happens if changed**:
- **Wrong host**: App can't connect to database, all API calls fail
- **Wrong port**: Connection refused error
- **Wrong credentials**: Authentication failed error
- **Wrong database name**: Database not found error
- **migrate_db = False**: Database structure won't update with new features

**Security considerations**:
```python
# NEVER put passwords directly in code!
# BAD:
db_pass = "agno9999!!"

# GOOD:
db_pass = getenv("DB_PASSWORD")  # Read from environment variable

# VERY GOOD:
# Store in AWS Secrets Manager and retrieve securely
```

#### **API Configuration**: `api/settings.py`

**Purpose**: Configure the web server and API behavior

**Each setting explained**:
```python
class ApiSettings(BaseSettings):
    # API identification
    title: str = "agent-api"               # Shows up in API documentation
    version: str = "1.0"                   # API version number
    
    # Environment type
    runtime_env: str = "dev"               # "dev", "stg", or "prd"
    
    # API documentation
    docs_enabled: bool = True              # True = /docs endpoint available
    
    # Cross-Origin Resource Sharing (security)
    cors_origin_list: Optional[List[str]] = None  # Which websites can call our API
```

**CORS explanation** (very important for security):
```python
# CORS controls which websites can call your API

# Example: Your API is at https://api.mycompany.com
# Without CORS: Only api.mycompany.com can call the API
# With CORS: You specify which other domains are allowed

cors_origin_list = [
    "https://app.agno.com",        # Agno playground can call our API
    "http://localhost:3000",       # Local development frontend
    "https://mycompany.com"        # Company website
]

# This prevents random websites from using your API without permission
```

#### **Environment Files**: `.env` and `example.env`

**Purpose**: Store sensitive configuration that shouldn't be in code

**File location**: `example.env` (template), `.env` (your actual values)

**Each setting explained**:
```bash
# AI Model API Keys
OPENAI_API_KEY=sk-proj-...           # For GPT models (fallback)
AWS_ACCESS_KEY_ID=AKIA...            # For Amazon Nova Lite (primary)
AWS_SECRET_ACCESS_KEY=XjZ8GTK...     # AWS secret key
AWS_REGION=us-east-1                 # AWS region for Nova Lite

# Monitoring and Analytics  
AGNO_API_KEY=ag-...                  # For Agno platform integration
AGNO_MONITOR=true                    # Enable monitoring

# Search Enhancement
EXA_API_KEY=your_exa_api_key         # For advanced web search
```

**Security considerations**:
```bash
# VERY IMPORTANT SECURITY RULES:

# 1. NEVER commit .env to Git
echo ".env" >> .gitignore

# 2. Use example.env as template (with fake values)
# example.env:
AWS_ACCESS_KEY_ID=your_aws_key_here

# 3. Real .env has actual values
# .env:
AWS_ACCESS_KEY_ID=AKIAYDWHTFFB4AQIJGWH

# 4. Rotate keys regularly
# 5. Use different keys for dev/staging/production
```

---

## Part 4: Why These Choices Were Made

### 4.1 Architecture Decisions

#### **Question**: Why use RDS instead of a simple file?

**Answer with examples**:

**Problems with files:**
```python
# Imagine storing chat history in a text file
chat_file = "conversations.txt"

# What happens with 1000 users chatting simultaneously?
user1_writes_to_file()    # File locked
user2_tries_to_write()    # ERROR: File in use
user3_tries_to_write()    # ERROR: File in use
# Result: 999 users can't use the chatbot!

# More problems:
# - Finding specific conversation: Read entire file (slow!)
# - Backup: Copy entire file (what if it corrupts during copy?)
# - Search: Read every line (impossible with millions of messages)
# - Crash during write: Entire file corrupted, all data lost
```

**Benefits of database:**
```python
# 1000 users can write simultaneously
user1_saves_message()    # ✅ Saved to row 1,000,001
user2_saves_message()    # ✅ Saved to row 1,000,002  
user3_saves_message()    # ✅ Saved to row 1,000,003
# All happen at the same time!

# Other benefits:
# - Find conversation: Use index, find in milliseconds
# - Backup: Automatic, continuous, point-in-time recovery
# - Search: Use SQL, find anything instantly
# - Crash during write: Only that one message affected, database recovers automatically
```

**Real scenario**: "What happens when 1000 users chat simultaneously?"

**With files:**
- 1 user succeeds, 999 users get errors
- Data corruption risk with each write
- System becomes unusable under load

**With database:**
- All 1000 users succeed  
- Each message safely isolated
- System scales to 10,000+ users

#### **Question**: Why use vector database for search?

**Answer with examples**:

**Keyword search (old way):**
```python
# User asks: "How do I reset my password?"
# Keyword search looks for: "reset" AND "password"

knowledge_base = [
    "To change your login credentials, go to settings",     # MISSED (no "reset" or "password")
    "Password recovery process starts in account menu",     # FOUND (has "password")
    "Reset account access through forgot password link"     # FOUND (has "reset" and "password")
]

# Problems:
# - Misses relevant info with different words
# - No understanding of meaning
# - Exact word matching only
```

**Semantic search (vector way):**
```python
# User asks: "How do I reset my password?"
# Vector search understands MEANING

user_question_vector = [0.2, 0.8, 0.1, ...]  # Vector for the question

knowledge_base_vectors = [
    [0.3, 0.7, 0.2, ...],  # "change login credentials" - SIMILAR meaning!
    [0.2, 0.8, 0.1, ...],  # "password recovery" - VERY similar!
    [0.2, 0.8, 0.1, ...],  # "reset account access" - VERY similar!
]

# Benefits:
# - Finds relevant info even with different words
# - Understands synonyms and context
# - Finds semantically related content
```

**Real scenario**: Search results comparison

**User question**: "I can't log into my account"

**Keyword search results:**
- Document 1: "Login troubleshooting guide" ✅
- Document 2: "Account access issues" ❌ (missed - no "login")
- Document 3: "Sign-in problems FAQ" ❌ (missed - no "login") 

**Vector search results:**
- Document 1: "Login troubleshooting guide" ✅  
- Document 2: "Account access issues" ✅ (found - similar meaning)
- Document 3: "Sign-in problems FAQ" ✅ (found - "sign-in" ≈ "login")

Vector search finds 3x more relevant results!

#### **Question**: Why this specific database structure?

**Answer with examples**:

**Alternative 1: Single giant table**
```sql
-- BAD: Everything in one table
CREATE TABLE everything (
    id SERIAL,
    user_id TEXT,
    agent_id TEXT,
    message TEXT,
    response TEXT,
    knowledge_content TEXT,
    knowledge_vector VECTOR(1536),
    team_member TEXT,
    workflow_step TEXT
    -- ... 50 more columns
);

-- Problems:
-- - Most columns empty for each row (wasted space)
-- - Slow queries (searching through irrelevant data)
-- - Hard to maintain (changing one feature breaks everything)
-- - No relationships between data
```

**Alternative 2: Too many small tables**
```sql
-- BAD: Over-engineered
CREATE TABLE users (...);
CREATE TABLE sessions (...);
CREATE TABLE messages (...);
CREATE TABLE responses (...);
CREATE TABLE agent_configs (...);
-- ... 20 more tables

-- Problems:
-- - Simple queries need 10+ table JOINs (very slow)
-- - Complex relationships hard to understand
-- - Over-engineering for simple use case
```

**Our approach: Balanced structure**
```sql
-- GOOD: Logical separation
-- Agent conversations
CREATE TABLE sage_sessions (...)      -- Fast agent queries
CREATE TABLE scholar_sessions (...)   -- Separate agent data

-- Knowledge base
CREATE TABLE sage_knowledge (...)     -- Vector search optimized

-- Team coordination  
CREATE TABLE finance_team (...)       -- Team-specific needs

-- Benefits:
-- - Each table optimized for its purpose
-- - Simple queries stay fast
-- - Easy to understand and maintain
-- - Can evolve independently
```

**Performance impact**:
```python
# Our structure performance:
find_user_conversation()     # 1 table scan = 5ms
search_knowledge_base()      # 1 vector search = 10ms  
get_agent_history()          # 1 index lookup = 2ms

# Single table performance:
find_user_conversation()     # Scan giant table = 500ms
search_knowledge_base()      # Scan irrelevant data = 1000ms
get_agent_history()          # Filter massive table = 200ms

# Our approach is 50-100x faster!
```

### 4.2 Technology Choices

#### **PostgreSQL Database**

**What it is**: Advanced relational database with AI/ML extensions

**Why we chose it**:
1. **Vector support**: PgVector extension for AI embeddings
2. **JSON support**: Store flexible metadata
3. **ACID compliance**: Data never corrupts
4. **Performance**: Handles millions of records efficiently
5. **Mature**: 30+ years of development, very stable

**Alternatives we considered**:
- **MySQL**: No vector support, less advanced features
- **MongoDB**: No strong consistency, harder to query
- **SQLite**: Single-user only, can't handle multiple connections

**Trade-offs**:
- **Gained**: Advanced features, scalability, AI capabilities
- **Lost**: Some simplicity (more complex than SQLite)

#### **FastAPI Framework**

**What it is**: Modern Python web framework for building APIs

**Why we chose it**:
1. **Automatic documentation**: `/docs` endpoint generated automatically
2. **Type safety**: Catches errors before they happen
3. **High performance**: As fast as Node.js, faster than Flask
4. **Modern Python**: Uses latest Python features (async/await)
5. **Easy testing**: Built-in test client

**Alternatives we considered**:
- **Flask**: Older, requires more setup, no automatic docs
- **Django**: Too heavy for API-only project, includes unnecessary features
- **Express.js**: Would require JavaScript, team knows Python better

**Trade-offs**:
- **Gained**: Speed, type safety, automatic documentation, modern features
- **Lost**: Some simplicity (steeper learning curve than Flask)

#### **Amazon Nova Lite AI Model**

**What it is**: Amazon's latest multimodal AI model

**Why we chose it**:
1. **Cost effective**: $0.06 per million tokens (vs $5+ for GPT-4)
2. **Fast**: Lightning-fast response times
3. **Multimodal**: Handles text, images, and video
4. **Large context**: 300K token context window
5. **AWS integration**: Native AWS services integration

**Alternatives we considered**:
- **OpenAI GPT-4**: More expensive, external dependency
- **Claude**: Good but more expensive, external API
- **Local models**: Would require expensive GPU hardware

**Trade-offs**:
- **Gained**: Cost savings, speed, AWS integration, multimodal capabilities
- **Lost**: Some brand recognition (GPT more well-known)

---

*[This is Part 2 of the complete guide. Part 3 will cover hands-on examples, troubleshooting, and maintenance.]* 