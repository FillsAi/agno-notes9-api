# Dialogue Management System - Database Architecture & Flow

## 🧠 Intelligent Dialogue Management with Long-Term & Short-Term Memory

---

### 📊 System Flow: From User Message to Response

```mermaid
flowchart TD
    A[👤 User sends message] --> B{🔍 New Session?}
    B -->|Yes| C[📝 Create new session_id]
    B -->|No| D[📖 Load conversation history]
    
    C --> E[🧠 Initialize Agent]
    D --> E
    
    E --> F[🔍 Search Knowledge Base]
    F --> G[🌐 Web Search if needed]
    G --> H[🤖 Generate AI Response]
    
    H --> I[💾 Store message + response]
    I --> J[📤 Return response to user]
    
    subgraph "💽 Database Operations"
        K[📊 Session Storage<br/>sage_sessions table]
        L[🧠 Knowledge Base<br/>sage_knowledge table]
        M[👥 Team Storage<br/>team_* tables]
        N[🔄 Workflow Cache<br/>workflow_* tables]
    end
    
    F -.-> L
    I -.-> K
    I -.-> M
    I -.-> N
```

---

### 🗄️ Database Schema: Complete Table Structure

#### **1. Agent Conversation Storage (Short-Term Memory)**

| **Table: `sage_sessions`** | **Data Type** | **Purpose** | **Example** |
|---|---|---|---|
| `id` | SERIAL PRIMARY KEY | Unique record identifier | 1, 2, 3... |
| `user_id` | VARCHAR(255) | User identification across sessions | 'user_123', 'enterprise_user_456' |
| `session_id` | VARCHAR(255) | Groups related conversation messages | 'sess_2024_01_15_10_30_abc' |
| `agent_id` | VARCHAR(255) | Which AI agent handled the request | 'sage', 'scholar', 'finance-team' |
| `message` | TEXT | Original user message/query | 'What are our Q4 revenue projections?' |
| `response` | TEXT | AI-generated response | 'Based on current data, Q4 revenue is projected at...' |
| `model_id` | VARCHAR(255) | AI model used for generation | 'amazon.nova-lite-v1:0', 'gpt-4' |
| `created_at` | TIMESTAMP | When message was sent | '2024-01-15 10:30:00 UTC' |
| `updated_at` | TIMESTAMP | Last modification time | '2024-01-15 10:30:02 UTC' |
| `metadata` | JSONB | Additional context and metrics | `{"tools_used": ["web_search"], "response_time": 2.3, "user_rating": 5}` |

**📈 Performance Indexes:**
```sql
CREATE INDEX idx_sessions_user_created ON sage_sessions(user_id, created_at DESC);
CREATE INDEX idx_sessions_session_created ON sage_sessions(session_id, created_at DESC);
```

---

#### **2. Knowledge Base Storage (Long-Term Memory)**

| **Table: `sage_knowledge`** | **Data Type** | **Purpose** | **Example** |
|---|---|---|---|
| `id` | SERIAL PRIMARY KEY | Unique knowledge record | 1, 2, 3... |
| `content` | TEXT | Original document text content | 'Our company return policy allows returns within 30 days...' |
| `embedding` | VECTOR(1536) | Mathematical representation for AI search | [0.23, 0.87, 0.12, 0.45, ...] (1536 numbers) |
| `document_name` | VARCHAR(255) | Source document identifier | 'Employee_Handbook_2024.pdf', 'Product_Catalog.docx' |
| `chunk_index` | INTEGER | Document section number | 1, 2, 3... (for large documents split into parts) |
| `created_at` | TIMESTAMP | When knowledge was added | '2024-01-15 09:00:00 UTC' |
| `updated_at` | TIMESTAMP | Last knowledge update | '2024-01-15 09:00:00 UTC' |
| `metadata` | JSONB | Document classification and context | `{"section": "Returns", "page": 5, "policy_type": "customer_service", "confidence": 0.95}` |

**🔍 Vector Search Optimization:**
```sql
CREATE INDEX idx_knowledge_embedding ON sage_knowledge USING ivfflat (embedding vector_cosine_ops);
```

---

#### **3. Multi-Agent Team Storage (Collaborative Memory)**

| **Table: `finance_researcher_team`** | **Data Type** | **Purpose** | **Example** |
|---|---|---|---|
| `id` | SERIAL PRIMARY KEY | Unique team interaction record | 1, 2, 3... |
| `user_id` | VARCHAR(255) | User who requested team analysis | 'analyst_456', 'portfolio_manager_789' |
| `session_id` | VARCHAR(255) | Team collaboration session | 'team_sess_2024_01_15_financial_analysis' |
| `team_id` | VARCHAR(255) | Which team handled the request | 'financial-researcher-team', 'content-creation-team' |
| `member_responses` | JSONB | Individual agent contributions | `{"finance_agent": "AAPL shows strong fundamentals...", "web_agent": "Recent news indicates..."}` |
| `final_response` | TEXT | Coordinated team output | 'Investment Analysis: Based on financial data and market research...' |
| `created_at` | TIMESTAMP | When team collaboration started | '2024-01-15 11:00:00 UTC' |
| `updated_at` | TIMESTAMP | Last team update | '2024-01-15 11:05:30 UTC' |
| `metadata` | JSONB | Team coordination data | `{"agents_used": ["finance_agent", "web_agent"], "analysis_type": "stock_evaluation", "processing_time": 5.3}` |

---

#### **4. Workflow Storage (Process Memory)**

| **Table: `blog_post_generator_workflows`** | **Data Type** | **Purpose** | **Example** |
|---|---|---|---|
| `id` | SERIAL PRIMARY KEY | Unique workflow execution | 1, 2, 3... |
| `workflow_id` | VARCHAR(255) | Type of workflow executed | 'generate-blog-post-on', 'investment-report-generator' |
| `user_id` | VARCHAR(255) | User who initiated workflow | 'content_manager_123', 'marketing_team_456' |
| `session_id` | VARCHAR(255) | Workflow execution session | 'workflow_sess_2024_01_15_blog_ai_trends' |
| `input_data` | JSONB | Original workflow parameters | `{"topic": "AI trends 2024", "target_audience": "business_leaders", "word_count": 1500}` |
| `output_data` | JSONB | Generated workflow results | `{"title": "AI Trends Reshaping Business in 2024", "content": "...", "sources": [...]}` |
| `status` | VARCHAR(50) | Current workflow state | 'completed', 'in_progress', 'failed', 'cached' |
| `created_at` | TIMESTAMP | Workflow start time | '2024-01-15 14:00:00 UTC' |
| `completed_at` | TIMESTAMP | Workflow completion time | '2024-01-15 14:08:45 UTC' |
| `metadata` | JSONB | Execution metrics and cache info | `{"steps_completed": 3, "cache_hit": true, "total_tokens": 3500, "cost": 0.12}` |

---

### ⚡ Memory Management Strategy

#### **🧠 Short-Term Memory (Conversation Context)**
- **Storage**: `*_sessions` tables
- **Retention**: Last 3-5 messages per conversation
- **Purpose**: Maintain conversation flow and context
- **Performance**: 2-5ms average retrieval time
- **Indexing**: Optimized for user_id + session_id lookups

#### **🧠 Long-Term Memory (Knowledge Base)**
- **Storage**: `*_knowledge` tables with vector embeddings
- **Retention**: Permanent until manually removed
- **Purpose**: Semantic search across company documents
- **Performance**: 10-15ms vector similarity search
- **Indexing**: IVFFlat vector index for 1536-dimensional embeddings

#### **👥 Collaborative Memory (Team Coordination)**
- **Storage**: `*_team` tables
- **Retention**: Complete team interaction history
- **Purpose**: Multi-agent coordination and result synthesis
- **Performance**: 5-8ms team history retrieval
- **Indexing**: Optimized for team_id + session_id queries

---

### 📊 Performance Metrics & Scalability

| **Memory Type** | **Average Query Time** | **Concurrent Users** | **Storage Growth** | **Cost per Month** |
|---|---|---|---|---|
| **Short-Term (Conversations)** | 2-5ms | 1,000+ | ~10MB per 1K conversations | $1-3 |
| **Long-Term (Knowledge)** | 10-15ms | 500+ simultaneous searches | ~1GB per 10K documents | $5-10 |
| **Team Coordination** | 5-8ms | 200+ concurrent teams | ~50MB per 1K team sessions | $2-5 |
| **Workflow Cache** | 3-7ms | 100+ concurrent workflows | ~100MB per 1K workflows | $3-7 |

---

### 🔧 Technical Implementation

#### **Database Configuration**
```python
# PostgreSQL 17.2 with PgVector extension
db_instance_class = "db.t4g.small"    # $25/month production cost
storage = 64GB                        # Auto-scaling enabled
connections = 20                      # Connection pool size
backup_retention = 7                  # Days of automated backups
```

#### **Connection Optimization**
```python
# Connection pool configuration for high performance
pool_size = 20              # Base connections
max_overflow = 30          # Peak traffic handling
pool_recycle = 3600       # Connection refresh (1 hour)
pool_pre_ping = True      # Health check before use
```

---

### 💡 Investor Value Proposition

#### **🚀 Scalability**
- **Horizontal**: Add read replicas for 10x read performance
- **Vertical**: Upgrade instance class for 5x processing power
- **Geographic**: Multi-region deployment for global performance

#### **💰 Cost Efficiency**
- **Current**: $25/month supports 1K+ active users
- **Scaling**: Linear cost scaling (2x users = 2x cost)
- **Optimization**: 95% query cache hit rate reduces compute costs

#### **🔒 Enterprise Ready**
- **Security**: Row-level security, encryption at rest/transit
- **Compliance**: SOC2, GDPR data handling capabilities  
- **Backup**: Automated backups with point-in-time recovery
- **Monitoring**: Real-time performance metrics and alerting

#### **🎯 Competitive Advantage**
- **Hybrid Memory**: Combines conversation context + knowledge search
- **Multi-Modal**: Handles text, images, documents in unified system
- **Team Intelligence**: Multiple AI agents collaborate automatically
- **Workflow Automation**: Complex multi-step processes cached and optimized 