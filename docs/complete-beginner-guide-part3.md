# Complete Beginner's Guide - Part 3: Hands-On Examples and Troubleshooting






# Complete Beginner's Guide to RDS and Database Concepts

## Overview
This guide explains databases, RDS, and how data flows in our AI Agent API project. We assume you know **NOTHING** about databases, programming, or technical concepts. Everything is explained with real examples from our actual codebase.

---

## Part 1: Basic Concepts (Explain Like I'm 5)

### 1.1 What is a Database?

#### **Real-world analogy**: Think of a Library
Imagine a massive library with millions of books. To find any book quickly, the library has:
- **Card catalogs** (indexes) that tell you exactly where each book is
- **Sections** (tables) organized by topic (Fiction, Science, History)
- **Librarians** (database engine) who know how to find anything instantly
- **Check-out system** (transactions) to track who borrowed what

#### **Simple definition**: What databases actually do
A database is a **smart filing system** that:
- **Stores information** in organized tables (like Excel sheets)
- **Finds information** super fast (even with millions of records)
- **Keeps information safe** (no corruption, automatic backups)
- **Handles multiple users** at the same time without conflicts

#### **Why we need them**: What happens without databases?
Without databases, our chatbot would be like a person with **no memory**:
- Every conversation starts from scratch
- No learning from previous interactions
- Can't remember user preferences
- Can't store knowledge documents
- Would break if multiple people use it simultaneously

#### **Example**: Simple table vs database table
```
Simple Excel Sheet:
| Name    | Email           | Message              |
|---------|-----------------|----------------------|
| John    | john@email.com  | Hi, how are you?     |
| Sarah   | sarah@email.com | What's the weather?  |

Our Database Table (much more powerful):
- Handles 1 million+ conversations simultaneously
- Finds any conversation in milliseconds  
- Automatically backs up every second
- Links conversations to users, sessions, and knowledge
```

#### **In this project**: What specific data does our database store?

Our Agent API database stores these main types of data:

1. **Chat Conversations**: Every message between users and the AI
2. **Knowledge Base**: Documents, PDFs, and information the AI can search
3. **User Sessions**: Who is talking to the chatbot and when
4. **Agent Memory**: What the AI learned from previous conversations
5. **Vector Embeddings**: Mathematical representations of text for smart search

### 1.2 What is RDS?

#### **Full form**: What does RDS stand for?
**RDS = Relational Database Service** (from Amazon Web Services)

#### **Simple explanation**: What is Amazon RDS in plain English?
RDS is like **hiring a professional database administrator** without actually hiring a person. Instead of you:
- Installing database software
- Configuring servers
- Managing backups
- Monitoring performance
- Fixing problems at 3 AM

Amazon does ALL of this for you automatically, 24/7.

#### **Why use RDS**: Why not just use a regular database?

**DIY Database (like building your own house):**
- You buy servers ($5,000+)
- You install PostgreSQL software (hours of work)
- You configure security (complex and error-prone)
- You set up backups (what if they fail?)
- Server crashes at midnight → your problem
- Cost: $5,000+ setup + $500+/month maintenance + your time

**RDS (like renting a luxury apartment):**
- Amazon provides everything pre-configured
- Professional monitoring 24/7
- Automatic backups every day
- Automatic security updates
- Server crashes → Amazon fixes it in minutes
- Cost: $25/month for our setup

#### **Analogy**: Compare to renting vs buying a house
**Buying a house (DIY Database):**
- Buy land, build house, install plumbing, electrical
- You fix everything when it breaks
- Huge upfront cost and ongoing maintenance

**Renting an apartment (RDS):**
- Move in immediately, everything works
- Landlord fixes problems
- Predictable monthly cost

#### **In this project**: Which specific RDS service are we using and why?

**Our RDS Configuration:**
- **Service**: Amazon RDS PostgreSQL 17.2
- **Instance**: db.t4g.small ($25/month)
- **Storage**: 64GB SSD
- **Why PostgreSQL**: Best for AI applications (supports vector search)
- **Why this size**: Perfect for development and small production use

**Location in code**: `workspace/prd_resources.py` lines 118-139

```python
prd_db = DbInstance(
    name=f"{ws_settings.prd_key}-db",
    group="db",
    db_name="ai",                    # Database name
    port=5432,                       # Standard PostgreSQL port
    engine="postgres",               # Database type
    engine_version="17.2",           # Latest version
    allocated_storage=64,            # 64GB storage
    db_instance_class="db.t4g.small", # Server size (~$25/month)
    publicly_accessible=True,        # Can connect from internet
    enable_performance_insights=True, # Monitoring enabled
)
```

### 1.3 What is a Chatbot?

#### **Basic definition**: What chatbots do
A chatbot is a **computer program that talks like a human**. It:
- Receives messages from users
- Understands what users are asking
- Finds or generates appropriate answers
- Responds in natural language

#### **How they work**: Simple explanation of input → processing → output
```
1. INPUT: User types "What's the weather in Tokyo?"
   ↓
2. PROCESSING: 
   - Understand: User wants weather information
   - Location: Tokyo
   - Search: Look up current weather data
   ↓
3. OUTPUT: "The current weather in Tokyo is 22°C, partly cloudy with light winds."
```

#### **Types of chatbots**:
1. **Rule-based**: Follows pre-written scripts (like old phone menus)
2. **AI-based**: Uses artificial intelligence to understand and respond (our system)

#### **In this project**: What type of chatbot do we have?

We have an **AI-powered agent system** with multiple specialized agents:

**Our Agents** (found in `/agents/` folder):
1. **Sage Agent** (`agents/sage.py`): Main AI agent with knowledge base and web search
2. **Scholar Agent** (`agents/scholar.py`): Research-focused agent for detailed analysis
3. **Team Agents** (`teams/`): Multiple agents working together

**Example from our code** (`agents/sage.py` lines 16-21):
```python
def get_sage(
    model_id: Optional[str] = None,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    debug_mode: bool = True,
) -> Agent:
```

### 1.4 What is a Vector Database?

#### **What are vectors**: Explain with simple examples
A **vector** is just a list of numbers that represents something's characteristics.

**Real-world examples:**
- **GPS coordinates**: [40.7128, -74.0060] represents New York City
- **Color**: [255, 0, 0] represents bright red
- **Person**: [height, weight, age] like [180, 75, 30]

#### **Why vectors for text**: How do we convert words to numbers?
Text is converted to vectors so computers can understand meaning:

**Words → Numbers example:**
- "dog" → [0.2, 0.8, 0.1, 0.9, ...]  (1536 numbers)
- "puppy" → [0.3, 0.7, 0.2, 0.8, ...] (very similar numbers!)
- "car" → [0.9, 0.1, 0.8, 0.2, ...]  (very different numbers)

#### **Simple analogy**: Like GPS coordinates for words
Just like GPS coordinates tell you which places are close to each other, word vectors tell you which words mean similar things.

#### **In this project**: What do we store as vectors and why?

**Our Vector Storage** (`agents/sage.py` lines 84-86):
```python
knowledge=AgentKnowledge(
    vector_db=PgVector(table_name="sage_knowledge", db_url=db_url, search_type=SearchType.hybrid)
),
```

**What we vectorize:**
1. **User questions**: To find similar previous questions
2. **Knowledge documents**: To find relevant information
3. **Conversation history**: To maintain context

**Why vectors help our chatbot:**
- User asks: "How do I reset my password?"
- Vector search finds similar questions: "password recovery", "login issues", "account access"
- Provides relevant answers even if exact words don't match

---

## Part 2: Step-by-Step Data Journey

### 2.1 Complete Flow with Real Example

Let's trace this exact scenario: **User asks "Hi, how can I check my order status online?"**

#### **Step 1**: User types question

**File involved**: `api/routes/agents.py` (lines 68-103)

**What happens**: User sends HTTP request to our API

**Code snippet**:
```python
@agents_router.post("/{agent_id}/runs", status_code=status.HTTP_200_OK)
async def run_agent(agent_id: AgentType, body: RunRequest):
    """
    Sends a message to a specific agent and returns the response.
    """
    logger.debug(f"RunRequest: {body}")
```

**Data at this point**:
```json
{
  "message": "Hi, how can I check my order status online?",
  "user_id": "user123",
  "session_id": "sess_456",
  "stream": false,
  "model": "amazon.nova-lite-v1:0"
}
```

**Explanation**: The user's message is packaged into a JSON request and sent to our `/v1/agents/sage/runs` endpoint.

#### **Step 2**: Processing the question

**File involved**: `agents/sage.py` (lines 16-101)

**Code snippet**:
```python
def get_sage(
    model_id: Optional[str] = None,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    debug_mode: bool = True,
) -> Agent:
    # Create explicit boto3 session and client
    session = boto3.Session()
    bedrock_client = session.client('bedrock-runtime', region_name=agent_settings.aws_region)
```

**What happens**: 
1. Creates an AI agent instance
2. Sets up connection to Amazon Nova Lite AI model
3. Loads user's conversation history from database
4. Prepares to process the message

**Data format**:
```python
# Before: Raw user input
message = "Hi, how can I check my order status online?"

# After: Structured agent request
agent_request = {
    "user_id": "user123",
    "session_id": "sess_456", 
    "message": "Hi, how can I check my order status online?",
    "context": "Previous conversation history...",
    "available_tools": ["web_search", "knowledge_base"]
}
```

#### **Step 3**: Searching for answer

**File involved**: `agents/sage.py` (lines 84-86)

**Database query**: The system searches the vector database for relevant knowledge

**Code snippet**:
```python
knowledge=AgentKnowledge(
    vector_db=PgVector(table_name="sage_knowledge", db_url=db_url, search_type=SearchType.hybrid)
),
```

**What happens**:
1. Converts user question to vector: [0.2, 0.8, 0.1, ...] (1536 numbers)
2. Searches knowledge base for similar vectors
3. Finds documents about "order tracking", "account management", "online services"
4. May also search the web for current information

**Example database query** (simplified):
```sql
SELECT content, similarity 
FROM sage_knowledge 
WHERE embedding <-> '[0.2,0.8,0.1,...]' < 0.5
ORDER BY similarity DESC 
LIMIT 5;
```

#### **Step 4**: Generating response

**File involved**: `api/routes/agents.py` (lines 95-103)

**Code snippet**:
```python
# Use synchronous run for reliability
response = agent.run(body.message, stream=False)
return {"content": response.content if response.content else "No response generated"}
```

**What happens**:
1. AI model (Amazon Nova Lite) processes the question + context + knowledge
2. Generates human-like response
3. Returns structured answer

**Data sent back**:
```json
{
  "content": "Hi! To check your order status online, you can:\n\n1. **Log into your account** on our website\n2. **Go to 'My Orders'** section\n3. **Find your order** and click for details\n4. **Track shipment** with the tracking number provided\n\nYou can also call customer service at 1-800-555-0123 for immediate assistance. Is there a specific order you need help tracking?"
}
```

#### **Step 5**: Saving conversation

**File involved**: `db/session.py` (lines 8-27)

**Code snippet**:
```python
# Create SQLAlchemy Engine using a database URL
db_url: str = db_settings.get_db_url()
db_engine: Engine = create_engine(db_url, pool_pre_ping=True)

def get_db() -> Generator[Session, None, None]:
    """Dependency to get a database session."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Database table**: Chat conversations are stored in tables like `sage_sessions`

**What gets stored**:
```sql
INSERT INTO sage_sessions (
    user_id,
    session_id,  
    message,
    response,
    timestamp,
    agent_id,
    model_used
) VALUES (
    'user123',
    'sess_456',
    'Hi, how can I check my order status online?',
    'Hi! To check your order status online, you can...',
    '2024-01-15 10:30:00',
    'sage',
    'amazon.nova-lite-v1:0'
);
```

**Why save it**: 
- Remember conversation context for follow-up questions
- Learn from user interactions
- Provide personalized responses
- Analytics and improvement

---

### 2.2 Knowledge Base Creation Example

Let's trace: **"Adding a company policy document (PDF) to the knowledge base"**

#### **Step 1**: Document upload

**File involved**: Currently handled by the Agno framework (external system)

**What happens**: 
1. User uploads a PDF file through web interface
2. File is temporarily stored in memory
3. System validates file type and size

**Example**: Uploading "Employee_Handbook_2024.pdf"

#### **Step 2**: Text extraction

**Technology used**: `newspaper4k` library (see `requirements.txt` line 43)

**Code snippet** (conceptual, handled by framework):
```python
from newspaper4k import Article

def extract_text_from_pdf(pdf_file):
    # Extract text content from PDF
    extracted_text = pdf_extractor.extract(pdf_file)
    return extracted_text
```

**What happens**:
- PDF is processed page by page
- Text is extracted and cleaned
- Formatting is preserved where important

**Example text extraction**:
```
Original PDF: [Complex formatting, images, tables]

Extracted Text: 
"Employee Handbook 2024
Chapter 1: Company Policies
1.1 Remote Work Policy
Employees may work remotely up to 3 days per week with manager approval..."
```

#### **Step 3**: Converting to vectors

**File involved**: Uses the PgVector system (see `agents/sage.py` lines 84-86)

**Code snippet**:
```python
# Text is split into chunks and converted to vectors
text_chunks = [
    "Remote Work Policy: Employees may work remotely up to 3 days per week...",
    "Vacation Policy: All employees receive 15 vacation days per year...",
    "Benefits: Company provides health insurance, dental, and vision..."
]

# Each chunk becomes a vector
for chunk in text_chunks:
    vector = embedding_model.encode(chunk)  # [0.2, 0.8, 0.1, ...] (1536 numbers)
    store_in_database(chunk, vector)
```

**What happens**:
1. Document is split into smaller chunks (paragraphs or sections)
2. Each chunk is converted to a vector using AI
3. Vectors capture the meaning of the text

**Example vector conversion**:
```
Text: "Remote work policy allows 3 days per week"
Vector: [0.23, 0.87, 0.12, 0.45, 0.67, ...] (1536 numbers total)

Text: "Vacation time is 15 days annually"  
Vector: [0.45, 0.23, 0.78, 0.12, 0.89, ...] (different pattern)
```

#### **Step 4**: Storing in database

**Database table**: `sage_knowledge` (vector database table)

**Code snippet** (simplified):
```sql
CREATE TABLE sage_knowledge (
    id SERIAL PRIMARY KEY,
    content TEXT,                          -- Original text chunk
    embedding VECTOR(1536),               -- Vector representation
    document_name VARCHAR(255),           -- "Employee_Handbook_2024.pdf"
    chunk_index INTEGER,                  -- Which part of document
    created_at TIMESTAMP,
    metadata JSONB                        -- Extra information
);
```

**What gets saved**:
```sql
INSERT INTO sage_knowledge (content, embedding, document_name, chunk_index, metadata) VALUES
(
    'Remote Work Policy: Employees may work remotely up to 3 days per week with manager approval. Requests must be submitted 48 hours in advance...',
    '[0.23,0.87,0.12,0.45,0.67,...]',
    'Employee_Handbook_2024.pdf',
    1,
    '{"section": "Remote Work", "page": 15, "policy_type": "work_arrangement"}'
),
(
    'Vacation Policy: All employees receive 15 vacation days per year. Additional days may be earned based on tenure...',
    '[0.45,0.23,0.78,0.12,0.89,...]',
    'Employee_Handbook_2024.pdf', 
    2,
    '{"section": "Time Off", "page": 23, "policy_type": "benefits"}'
);
```

**Benefits of this storage method**:
- **Fast search**: Find relevant information in milliseconds
- **Semantic search**: Finds meaning, not just keywords
- **Context preservation**: Maintains relationship between pieces of information
- **Scalable**: Can handle millions of documents

Now when a user asks "Can I work from home?", the system:
1. Converts question to vector
2. Finds similar vectors in knowledge base
3. Returns relevant policy information
4. AI generates personalized response

This is how our chatbot "knows" about company policies without being explicitly programmed with that information!

---

*[This is Part 1 of the complete guide. The remaining parts will cover database tables, API endpoints, configuration files, troubleshooting, and hands-on examples.]*

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


## Part 5: Hands-On Examples

### 5.1 Setting Up Locally

#### **Complete tutorial**:

#### **Step 1: Prerequisites**

**What software needs to be installed?**

```bash
# 1. Python 3.11+ (check version)
python --version
# Should show: Python 3.11.x or higher

# 2. Git (for cloning the repository)
git --version

# 3. Docker (for running the database)
docker --version

# 4. Docker Compose (usually included with Docker)
docker-compose --version
```

**If anything is missing:**
```bash
# Install Python (macOS)
brew install python@3.11

# Install Python (Ubuntu/Debian)
sudo apt update && sudo apt install python3.11 python3.11-pip

# Install Docker (macOS)
brew install docker docker-compose

# Install Docker (Ubuntu/Debian)
sudo apt install docker.io docker-compose
```

#### **Step 2: Database setup**

**Local Development Database (using Docker):**

**File location**: `workspace/dev_resources.py` lines 25-32

```python
# This configuration automatically creates a PostgreSQL database
dev_db = PgVectorDb(
    name=f"{ws_settings.ws_name}-db",  # Creates "agent-api-db" container
    pg_user="ai",                      # Username: ai
    pg_password="ai",                  # Password: ai
    pg_database="ai",                  # Database name: ai
    host_port=5432,                    # Accessible on localhost:5432
)
```

**Start the database:**
```bash
# From your project root directory
docker-compose up -d db  # Start only the database
# OR using the agno framework
ag ws up --build dev_db  # Start using project configuration
```

**Verify database is running:**
```bash
# Check if container is running
docker ps
# Should show a container named "agent-api-db"

# Test connection
docker exec -it agent-api-db psql -U ai -d ai
# If successful, you'll see PostgreSQL prompt: ai=#
# Type \q to exit
```

#### **Step 3: Code setup**

**Clone and setup:**
```bash
# 1. Clone the repository
git clone https://github.com/your-username/agent-api.git
cd agent-api

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Copy environment template
cp example.env .env
```

**Edit your `.env` file:**
```bash
# Open .env in your text editor and add your actual values:

# AWS Bedrock Configuration (for Amazon Nova Lite)
AWS_ACCESS_KEY_ID=your_actual_aws_key_here
AWS_SECRET_ACCESS_KEY=your_actual_aws_secret_here
AWS_REGION=us-east-1

# Optional: OpenAI as fallback
OPENAI_API_KEY=sk-your-openai-key-here

# Optional: Advanced search
EXA_API_KEY=your_exa_key_here

# Optional: Monitoring
AGNO_API_KEY=your_agno_key_here
```

#### **Step 4: Database Migration**

**Run migrations to create tables:**
```bash
# Make sure database is running first
docker ps | grep agent-api-db

# Run database migrations
alembic -c db/alembic.ini upgrade head

# Should output:
# INFO [alembic.runtime.migration] Context impl PostgreSQLImpl.
# INFO [alembic.runtime.migration] Will assume transactional DDL.
# INFO [alembic.runtime.migration] Running upgrade  -> <revision_id>, Initial migration
```

#### **Step 5: Start the application**

**Method 1: Direct Python (simplest)**
```bash
# Start the FastAPI server
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Should output:
# INFO:     Uvicorn running on http://0.0.0.0:8000
# INFO:     Application startup complete.
```

**Method 2: Using Docker (production-like)**
```bash
# Build and run the full application
docker-compose up --build

# Or using agno framework
ag ws up --build
```

#### **Step 6: Verification**

**Test that everything works:**

```bash
# 1. Check API health
curl http://localhost:8000/v1/health

# Expected response:
# {
#   "status": "success",
#   "router": "status",
#   "path": "/health",
#   "utc": "2024-01-15T10:30:00.000Z"
# }

# 2. List available agents
curl http://localhost:8000/v1/agents

# Expected response:
# ["sage", "scholar", "test_sage"]

# 3. Test chat
curl -X POST "http://localhost:8000/v1/agents/sage/runs" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello! Can you help me?",
    "user_id": "test_user",
    "session_id": "test_session",
    "stream": false
  }'

# Expected response:
# {
#   "content": "Hello! I'd be happy to help you. I'm Sage, an AI agent with access to a knowledge base and web search capabilities. What would you like assistance with today?"
# }
```

**Open API documentation:**
```bash
# Visit in your browser:
http://localhost:8000/docs

# You should see interactive API documentation
# Try the endpoints directly from the web interface
```

### 5.2 Making Changes

#### **Example**: "Adding a new field to store user ratings"

Let's add the ability for users to rate AI responses.

#### **Step 1: Database change**

**Create migration file:**
```bash
# Generate migration
alembic -c db/alembic.ini revision --autogenerate -m "Add user rating to conversations"

# This creates a new file in db/migrations/versions/
# Something like: 001_add_user_rating_to_conversations.py
```

**Edit the migration file** (example path: `db/migrations/versions/001_add_user_rating.py`):
```python
def upgrade() -> None:
    # Add rating column to all session tables
    op.add_column('sage_sessions', sa.Column('user_rating', sa.Integer(), nullable=True))
    op.add_column('scholar_sessions', sa.Column('user_rating', sa.Integer(), nullable=True))
    
    # Add index for faster queries on ratings
    op.create_index('idx_sage_sessions_rating', 'sage_sessions', ['user_rating'])

def downgrade() -> None:
    # Remove the changes if we need to rollback
    op.drop_index('idx_sage_sessions_rating')
    op.drop_column('sage_sessions', 'user_rating')
    op.drop_column('scholar_sessions', 'user_rating')
```

**Apply the migration:**
```bash
alembic -c db/alembic.ini upgrade head

# Output:
# INFO [alembic.runtime.migration] Running upgrade xxx -> 001, Add user rating to conversations
```

#### **Step 2: Code changes**

**Which files need updating?**

**File 1**: `api/routes/agents.py` (add rating endpoint)

Add after the existing endpoints (around line 104):
```python
class RatingRequest(BaseModel):
    """Request model for rating a conversation"""
    conversation_id: int
    rating: int = Field(..., ge=1, le=5, description="Rating from 1-5 stars")
    feedback: Optional[str] = None

@agents_router.post("/{agent_id}/rate", status_code=status.HTTP_200_OK)
async def rate_conversation(agent_id: AgentType, body: RatingRequest):
    """
    Rate an AI agent's response
    
    Args:
        agent_id: The ID of the agent
        body: Rating information
        
    Returns:
        Success confirmation
    """
    try:
        # Get database session
        from db.session import get_db
        db = next(get_db())
        
        # Update the conversation with rating
        # This is simplified - actual implementation would depend on your ORM
        update_query = f"""
            UPDATE {agent_id}_sessions 
            SET user_rating = {body.rating}
            WHERE id = {body.conversation_id}
        """
        db.execute(update_query)
        db.commit()
        
        return {
            "status": "success",
            "message": f"Rating {body.rating} saved for conversation {body.conversation_id}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save rating: {str(e)}")
```

**File 2**: Update the main chat endpoint to return conversation IDs

**Modify** `api/routes/agents.py` lines 95-103:
```python
# OLD CODE:
response = agent.run(body.message, stream=False)
return {"content": response.content if response.content else "No response generated"}

# NEW CODE:
response = agent.run(body.message, stream=False)

# Get the conversation ID from the database
# (This would require extending the agent storage to return the ID)
conversation_id = response.conversation_id if hasattr(response, 'conversation_id') else None

return {
    "content": response.content if response.content else "No response generated",
    "conversation_id": conversation_id,  # NEW: Include ID for rating
    "can_rate": conversation_id is not None  # NEW: Show if rating is possible
}
```

#### **Step 3: Testing**

**Test the new rating feature:**
```bash
# 1. Send a message first
curl -X POST "http://localhost:8000/v1/agents/sage/runs" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is Python?",
    "user_id": "test_user",
    "session_id": "test_session"
  }'

# Response should now include conversation_id:
# {
#   "content": "Python is a programming language...",
#   "conversation_id": 123,
#   "can_rate": true
# }

# 2. Rate the response
curl -X POST "http://localhost:8000/v1/agents/sage/rate" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": 123,
    "rating": 5,
    "feedback": "Very helpful explanation!"
  }'

# Expected response:
# {
#   "status": "success", 
#   "message": "Rating 5 saved for conversation 123"
# }
```

**Verify in database:**
```bash
# Connect to database
docker exec -it agent-api-db psql -U ai -d ai

# Check the rating was saved
SELECT id, message, response, user_rating FROM sage_sessions WHERE id = 123;

# Should show:
# id  | message           | response                    | user_rating
# 123 | What is Python?   | Python is a programming...  | 5
```

### 5.3 Common Operations

#### **Adding new knowledge to the system**

**Example**: Add a company FAQ document

**Method 1: Using the API (if knowledge upload is implemented)**
```bash
# Upload a document (conceptual - would need file upload endpoint)
curl -X POST "http://localhost:8000/v1/knowledge/upload" \
  -F "file=@company_faq.pdf" \
  -F "agent_id=sage"
```

**Method 2: Direct database insertion (for testing)**
```python
# Create a script: add_knowledge.py
from db.session import db_engine
from sqlalchemy import text

def add_knowledge_chunk(content, document_name, metadata=None):
    """Add a piece of knowledge to the sage knowledge base"""
    
    # This is simplified - real implementation would use vector embeddings
    with db_engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO sage_knowledge (content, document_name, metadata, created_at)
            VALUES (:content, :doc_name, :metadata, NOW())
        """), {
            "content": content,
            "doc_name": document_name, 
            "metadata": metadata or "{}"
        })
        conn.commit()

# Usage
add_knowledge_chunk(
    content="Our support hours are Monday-Friday 9 AM to 5 PM EST.",
    document_name="company_faq.pdf",
    metadata='{"section": "support", "topic": "hours"}'
)

add_knowledge_chunk(
    content="To reset your password, click the 'Forgot Password' link on the login page.",
    document_name="company_faq.pdf", 
    metadata='{"section": "account", "topic": "password_reset"}'
)
```

#### **Retrieving chat history for a user**

```python
# Create script: get_user_history.py
from db.session import db_engine
from sqlalchemy import text
import json

def get_user_conversations(user_id, agent_id="sage", limit=10):
    """Get recent conversations for a user"""
    
    with db_engine.connect() as conn:
        result = conn.execute(text(f"""
            SELECT 
                session_id,
                message,
                response,
                created_at,
                user_rating
            FROM {agent_id}_sessions
            WHERE user_id = :user_id
            ORDER BY created_at DESC
            LIMIT :limit
        """), {"user_id": user_id, "limit": limit})
        
        conversations = []
        for row in result:
            conversations.append({
                "session_id": row.session_id,
                "message": row.message,
                "response": row.response,
                "timestamp": row.created_at.isoformat(),
                "rating": row.user_rating
            })
        
        return conversations

# Usage
user_history = get_user_conversations("test_user")
print(json.dumps(user_history, indent=2))
```

#### **Updating user preferences**

```python
# Add to API: api/routes/users.py (new file)
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any

users_router = APIRouter(prefix="/users", tags=["Users"])

class UserPreferences(BaseModel):
    preferred_agent: str = "sage"
    language: str = "en"
    response_style: str = "detailed"  # "brief", "detailed", "conversational"
    enable_web_search: bool = True
    
@users_router.post("/{user_id}/preferences")
async def update_user_preferences(user_id: str, preferences: UserPreferences):
    """Update user preferences"""
    
    # Store in database (could be in a user_preferences table)
    from db.session import db_engine
    from sqlalchemy import text
    
    with db_engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO user_preferences (user_id, preferences, updated_at)
            VALUES (:user_id, :prefs, NOW())
            ON CONFLICT (user_id) 
            DO UPDATE SET preferences = :prefs, updated_at = NOW()
        """), {
            "user_id": user_id,
            "prefs": preferences.model_dump_json()
        })
        conn.commit()
    
    return {"status": "success", "message": "Preferences updated"}

@users_router.get("/{user_id}/preferences")
async def get_user_preferences(user_id: str):
    """Get user preferences"""
    
    with db_engine.connect() as conn:
        result = conn.execute(text("""
            SELECT preferences FROM user_preferences WHERE user_id = :user_id
        """), {"user_id": user_id})
        
        row = result.fetchone()
        if row:
            return json.loads(row.preferences)
        else:
            # Return defaults
            return UserPreferences().model_dump()
```

#### **Deleting old conversations**

```python
# Create script: cleanup_old_data.py
from db.session import db_engine
from sqlalchemy import text
from datetime import datetime, timedelta

def cleanup_old_conversations(days_old=30, agent_id="sage"):
    """Delete conversations older than specified days"""
    
    cutoff_date = datetime.now() - timedelta(days=days_old)
    
    with db_engine.connect() as conn:
        # First, see how many will be deleted
        count_result = conn.execute(text(f"""
            SELECT COUNT(*) FROM {agent_id}_sessions 
            WHERE created_at < :cutoff
        """), {"cutoff": cutoff_date})
        
        count = count_result.scalar()
        print(f"Will delete {count} conversations older than {days_old} days")
        
        if count > 0:
            # Delete the old conversations
            conn.execute(text(f"""
                DELETE FROM {agent_id}_sessions 
                WHERE created_at < :cutoff
            """), {"cutoff": cutoff_date})
            conn.commit()
            print(f"Deleted {count} old conversations")
        else:
            print("No old conversations to delete")

# Usage
cleanup_old_conversations(days_old=90)  # Delete conversations older than 90 days
```

---

## Part 6: Troubleshooting Guide

### 6.1 Common Problems

#### **Problem**: "Chatbot gives wrong answers"

**Possible causes**:
1. **Outdated knowledge base**: AI is using old information
2. **Poor vector search**: Relevant knowledge not being found
3. **AI model issue**: Model making incorrect inferences
4. **Context confusion**: Mixed up conversation history
5. **Missing knowledge**: Information simply not in knowledge base

**How to debug**:

**Step 1: Check knowledge base**
```python
# Script: debug_knowledge.py
from db.session import db_engine
from sqlalchemy import text

def search_knowledge(query, agent_id="sage"):
    """Search what knowledge exists for a query"""
    
    with db_engine.connect() as conn:
        # Simple text search (not vector search)
        result = conn.execute(text(f"""
            SELECT content, document_name, metadata
            FROM {agent_id}_knowledge
            WHERE content ILIKE :query
            LIMIT 5
        """), {"query": f"%{query}%"})
        
        results = list(result)
        print(f"Found {len(results)} knowledge chunks for '{query}':")
        
        for i, row in enumerate(results):
            print(f"\n{i+1}. Document: {row.document_name}")
            print(f"   Content: {row.content[:200]}...")
            print(f"   Metadata: {row.metadata}")

# Usage
search_knowledge("password reset")
search_knowledge("support hours")
```

**Step 2: Check conversation history**
```python
def debug_conversation(user_id, session_id, agent_id="sage"):
    """See full conversation context"""
    
    with db_engine.connect() as conn:
        result = conn.execute(text(f"""
            SELECT message, response, created_at, metadata
            FROM {agent_id}_sessions
            WHERE user_id = :user_id AND session_id = :session_id
            ORDER BY created_at ASC
        """), {"user_id": user_id, "session_id": session_id})
        
        print(f"Conversation history for {user_id} in session {session_id}:")
        
        for row in result:
            print(f"\n[{row.created_at}]")
            print(f"User: {row.message}")
            print(f"Bot: {row.response}")
            if row.metadata:
                print(f"Meta: {row.metadata}")

# Usage
debug_conversation("user123", "sess_456")
```

**Step 3: Test AI model directly**
```python
# Script: test_ai_model.py
from agents.sage import get_sage

def test_model_response(question):
    """Test what the AI model says without any context"""
    
    # Create fresh agent (no conversation history)
    agent = get_sage(debug_mode=True)
    
    # Clear any existing context
    agent.clear_history()
    
    response = agent.run(question, stream=False)
    
    print(f"Question: {question}")
    print(f"Answer: {response.content}")
    print(f"Tools used: {getattr(response, 'tools_used', 'none')}")

# Usage
test_model_response("What are your support hours?")
test_model_response("How do I reset my password?")
```

**How to fix**:

**Solution 1: Update knowledge base**
```python
# If knowledge is missing or outdated
add_knowledge_chunk(
    content="Support hours: Monday-Friday 9 AM to 6 PM EST, Saturday 10 AM to 2 PM EST",
    document_name="updated_support_info.txt",
    metadata='{"updated": "2024-01-15", "section": "support_hours"}'
)
```

**Solution 2: Improve vector search**
```python
# Check if vector search is working
from agents.sage import get_sage

agent = get_sage()
# This would show what knowledge is being found for queries
# (Would need to extend agent to show search results)
```

**Solution 3: Check AI model configuration**
```python
# In agents/sage.py, verify model settings
model_id = model_id or agent_settings.nova_lite  # Should be "amazon.nova-lite-v1:0"

# Check if AWS credentials are working
import boto3
try:
    client = boto3.client('bedrock-runtime', region_name='us-east-1')
    # Test if we can access the model
    print("AWS Bedrock connection: OK")
except Exception as e:
    print(f"AWS Bedrock connection failed: {e}")
```

#### **Problem**: "Database connection fails"

**Possible causes**:
1. **Database not running**: Docker container stopped
2. **Wrong credentials**: Username/password incorrect
3. **Network issue**: Can't reach database host
4. **Port conflict**: Something else using port 5432
5. **Database corrupted**: Database files damaged

**How to diagnose**:

**Step 1: Check if database container is running**
```bash
# List running containers
docker ps

# Should show something like:
# CONTAINER ID   IMAGE          COMMAND                  PORTS
# abc123def456   postgres:15    "docker-entrypoint.s…"  0.0.0.0:5432->5432/tcp

# If not running, check all containers (including stopped)
docker ps -a

# If container exists but stopped, start it
docker start agent-api-db

# If container doesn't exist, recreate it
docker-compose up -d db
```

**Step 2: Test direct database connection**
```bash
# Try to connect directly
docker exec -it agent-api-db psql -U ai -d ai

# If this fails, check the container logs
docker logs agent-api-db

# Common error messages:
# "role 'ai' does not exist" → User not created
# "database 'ai' does not exist" → Database not created
# "Connection refused" → Database not accepting connections
```

**Step 3: Check application database settings**
```python
# Script: test_db_connection.py
from db.settings import db_settings
from db.session import db_engine
from sqlalchemy import text

def test_database_connection():
    """Test if application can connect to database"""
    
    print(f"Database URL: {db_settings.get_db_url()}")
    
    try:
        with db_engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✅ Database connection successful")
            print(f"PostgreSQL version: {version}")
            
            # Test if required tables exist
            result = conn.execute(text("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            tables = [row[0] for row in result]
            print(f"Available tables: {tables}")
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        
        # Provide specific troubleshooting
        error_str = str(e).lower()
        if "connection refused" in error_str:
            print("→ Database is not running or not accepting connections")
        elif "authentication failed" in error_str:
            print("→ Wrong username or password")
        elif "database" in error_str and "does not exist" in error_str:
            print("→ Database name is incorrect")
        elif "timeout" in error_str:
            print("→ Network issue or database overloaded")

# Usage
test_database_connection()
```

**How to fix**:

**Solution 1: Restart database**
```bash
# Stop and restart database container
docker-compose down db
docker-compose up -d db

# Wait a few seconds for startup
sleep 5

# Test connection
docker exec -it agent-api-db psql -U ai -d ai -c "SELECT 1;"
```

**Solution 2: Reset database (if corrupted)**
```bash
# WARNING: This deletes all data!
docker-compose down
docker volume rm agent-api_postgres_data  # Remove data volume
docker-compose up -d db

# Wait for startup
sleep 10

# Recreate tables
alembic -c db/alembic.ini upgrade head
```

**Solution 3: Check environment variables**
```bash
# Verify database connection settings
cat .env | grep DB_

# Should show:
# DB_HOST=localhost
# DB_PORT=5432
# DB_USER=ai
# DB_PASS=ai
# DB_DATABASE=ai

# If using Docker, make sure the database container name matches
docker inspect agent-api-db | grep '"Name"'
```

### 6.2 Monitoring and Maintenance

#### **What to monitor**:

**Key metrics and why they matter**:

1. **API Response Time**: How fast the chatbot responds
   - **Good**: < 2 seconds
   - **Warning**: 2-5 seconds
   - **Critical**: > 5 seconds

2. **Database Connection Pool**: How many database connections are in use
   - **Good**: < 80% of pool size
   - **Warning**: 80-95% 
   - **Critical**: > 95% (new requests will fail)

3. **Memory Usage**: How much RAM the application uses
   - **Good**: < 1GB for development
   - **Warning**: 1-2GB
   - **Critical**: > 2GB (may crash)

4. **Error Rate**: Percentage of API calls that fail
   - **Good**: < 1% errors
   - **Warning**: 1-5% errors
   - **Critical**: > 5% errors

#### **How to monitor**:

**Create monitoring script**: `monitor_system.py`
```python
import time
import psutil
import requests
from db.session import db_engine
from sqlalchemy import text

def check_api_health():
    """Check if API is responding"""
    try:
        response = requests.get("http://localhost:8000/v1/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {"status": "ok", "response_time": response.elapsed.total_seconds()}
        else:
            return {"status": "error", "code": response.status_code}
    except Exception as e:
        return {"status": "error", "error": str(e)}

def check_database_health():
    """Check database connection and performance"""
    try:
        start_time = time.time()
        with db_engine.connect() as conn:
            # Test query
            result = conn.execute(text("SELECT COUNT(*) FROM sage_sessions"))
            count = result.scalar()
            query_time = time.time() - start_time
            
            # Check connection pool
            pool = db_engine.pool
            pool_status = {
                "size": pool.size(),
                "checked_out": pool.checkedout(),
                "overflow": pool.overflow(),
                "checked_in": pool.checkedin()
            }
            
            return {
                "status": "ok",
                "query_time": query_time,
                "total_conversations": count,
                "pool": pool_status
            }
    except Exception as e:
        return {"status": "error", "error": str(e)}

def check_system_resources():
    """Check system CPU, memory, disk usage"""
    return {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage('/').percent,
        "load_average": psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else None
    }

def monitor_system():
    """Complete system health check"""
    print("=== System Health Check ===")
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # API Health
    api_health = check_api_health()
    print(f"\n📡 API Health: {api_health['status']}")
    if api_health['status'] == 'ok':
        print(f"   Response time: {api_health['response_time']:.3f}s")
    else:
        print(f"   Error: {api_health.get('error', api_health.get('code'))}")
    
    # Database Health
    db_health = check_database_health()
    print(f"\n🗄️  Database Health: {db_health['status']}")
    if db_health['status'] == 'ok':
        print(f"   Query time: {db_health['query_time']:.3f}s")
        print(f"   Total conversations: {db_health['total_conversations']}")
        pool = db_health['pool']
        print(f"   Connection pool: {pool['checked_out']}/{pool['size']} used")
    else:
        print(f"   Error: {db_health.get('error')}")
    
    # System Resources
    resources = check_system_resources()
    print(f"\n💻 System Resources:")
    print(f"   CPU: {resources['cpu_percent']:.1f}%")
    print(f"   Memory: {resources['memory_percent']:.1f}%")
    print(f"   Disk: {resources['disk_percent']:.1f}%")
    if resources['load_average']:
        print(f"   Load: {resources['load_average']:.2f}")
    
    print("\n" + "="*30)

# Usage
if __name__ == "__main__":
    monitor_system()
```

**Run monitoring:**
```bash
# One-time check
python monitor_system.py

# Continuous monitoring (every 30 seconds)
while true; do
    python monitor_system.py
    sleep 30
done
```

#### **Regular tasks**:

**Daily tasks:**
```bash
# Check logs for errors
docker logs agent-api-db | grep ERROR
docker logs agent-api | grep ERROR

# Check disk space
df -h

# Monitor active conversations
echo "SELECT COUNT(*) FROM sage_sessions WHERE created_at > NOW() - INTERVAL '24 hours';" | \
  docker exec -i agent-api-db psql -U ai -d ai
```

**Weekly tasks:**
```python
# Script: weekly_maintenance.py
def weekly_maintenance():
    """Tasks to run weekly"""
    
    # 1. Clean up old logs
    import os
    import glob
    from datetime import datetime, timedelta
    
    log_files = glob.glob("logs/*.log")
    cutoff = datetime.now() - timedelta(days=7)
    
    for log_file in log_files:
        file_time = datetime.fromtimestamp(os.path.getmtime(log_file))
        if file_time < cutoff:
            os.remove(log_file)
            print(f"Deleted old log: {log_file}")
    
    # 2. Database statistics
    with db_engine.connect() as conn:
        # Table sizes
        result = conn.execute(text("""
            SELECT 
                schemaname,
                tablename,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
            FROM pg_tables 
            WHERE schemaname = 'public'
            ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
        """))
        
        print("Database table sizes:")
        for row in result:
            print(f"  {row.tablename}: {row.size}")
    
    # 3. Performance statistics
    with db_engine.connect() as conn:
        result = conn.execute(text("""
            SELECT 
                COUNT(*) as total_conversations,
                COUNT(DISTINCT user_id) as unique_users,
                AVG(user_rating) as avg_rating
            FROM sage_sessions
            WHERE created_at > NOW() - INTERVAL '7 days'
        """))
        
        row = result.fetchone()
        print(f"\nWeekly stats:")
        print(f"  Total conversations: {row.total_conversations}")
        print(f"  Unique users: {row.unique_users}")
        print(f"  Average rating: {row.avg_rating:.2f}" if row.avg_rating else "No ratings")

# Usage
weekly_maintenance()
```

**Monthly tasks:**
```bash
# Update dependencies
pip list --outdated

# Database vacuum (cleanup and optimize)
echo "VACUUM ANALYZE;" | docker exec -i agent-api-db psql -U ai -d ai

# Backup database
docker exec agent-api-db pg_dump -U ai ai > backup_$(date +%Y%m%d).sql

# Check backup
head -20 backup_$(date +%Y%m%d).sql
```

#### **Performance optimization**:

**Database optimization:**
```sql
-- Add indexes for common queries
CREATE INDEX IF NOT EXISTS idx_sage_sessions_user_created 
    ON sage_sessions(user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_sage_sessions_session_created 
    ON sage_sessions(session_id, created_at DESC);

-- Update table statistics
ANALYZE sage_sessions;
ANALYZE sage_knowledge;
```

**Application optimization:**
```python
# In db/session.py, tune connection pool
db_engine: Engine = create_engine(
    db_url, 
    pool_pre_ping=True,
    pool_size=20,           # Increase from default 5
    max_overflow=30,        # Allow more connections during spikes
    pool_recycle=3600       # Recycle connections every hour
)
```

**Memory optimization:**
```python
# In agents/sage.py, limit conversation history
add_history_to_messages=True,
num_history_responses=3,    # Reduce from default 10 to save memory
```

This completes the comprehensive beginner's guide! You now have:

1. **Complete understanding** of databases, RDS, and how your Agent API works
2. **Real code examples** from your actual project
3. **Step-by-step setup instructions** for local development
4. **Troubleshooting guides** for common problems
5. **Monitoring and maintenance** procedures

You can now confidently:
- Set up the entire system from scratch
- Modify existing features
- Debug problems when they occur
- Monitor system health
- Explain how everything works to others

The system is production-ready and scalable from development to enterprise use!