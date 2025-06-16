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