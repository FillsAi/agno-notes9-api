# AI Agent API - Technical Architecture Components

---

## Slide 1: Master-ASTRA
### Agent Orchestration Technology Stack

**🏗️ Core Framework**
- **Framework**: Agno v1.4.6 Python framework with built-in agent orchestration
- **Agent Class**: Uses agno.agent.Agent as base class for all specialized agents
- **Memory**: AgentMemory system maintains conversation context across interactions
- **Storage**: PostgresAgentStorage handles persistent session data in PostgreSQL

**🤖 Agent Implementation**
- **Sage Agent**: Primary conversational agent with web search and knowledge base access
- **Session Management**: Boto3 session creates dedicated Bedrock runtime client
- **Tool Integration**: DuckDuckGoTools provides web search capabilities
- **Database Storage**: Each agent stores conversations in dedicated PostgreSQL tables

**📡 API Layer**
- **Framework**: FastAPI with async/await support for concurrent request handling
- **Endpoints**: RESTful `/v1/agents/{agent_id}/runs` pattern for agent interactions
- **Streaming**: AsyncGenerator yields real-time response chunks for live conversations
- **Models**: Pydantic BaseModel enforces request/response validation and type safety

---

## Slide 2: Planning LLM
### Claude 3.5 Sonnet on Amazon Bedrock

**🧠 Model Configuration**
- **Primary Model**: Claude 3.5 Sonnet (anthropic.claude-3-5-sonnet-20241022-v2:0)
- **Fallback Model**: Amazon Nova Lite (amazon.nova-lite-v1:0) for cost optimization
- **Region**: us-east-1 for optimal Bedrock service availability
- **Client**: Dedicated boto3 bedrock-runtime client with explicit session management

**⚙️ AWS Services**
- **Service**: Amazon Bedrock provides managed AI model inference
- **Authentication**: IAM credentials via AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY
- **SDK**: boto3 Python SDK handles API communication and authentication
- **Pricing**: Input tokens cost $0.003 per 1K, output tokens cost $0.015 per 1K

**🔧 Implementation Details**
- **Library**: agno[aws]==1.4.6 provides Bedrock integration with async support
- **Client Management**: Explicit boto3 client initialization prevents async runtime warnings
- **Streaming**: Synchronous streaming via agent.run() with stream=True parameter

---

## Slide 3: Dialogue Management
### PostgreSQL + FastAPI Session Management

**🗄️ Database Schema**
- **Table**: sage_sessions stores all conversation history with UUID primary keys
- **Session Tracking**: user_id and session_id combination enables multi-user support
- **Message Storage**: Separate message and response columns for conversation flow
- **Metadata**: model_id tracks which AI model generated each response

**📡 API Implementation**
- **Endpoint**: POST `/v1/agents/{agent_id}/runs` handles all agent interactions
- **Request Processing**: RunRequest Pydantic model validates incoming messages
- **Streaming Support**: StreamingResponse with text/plain media type for real-time chat
- **Response Modes**: Both streaming and non-streaming response options available

**🔧 Technology Stack**
- **Database**: PostgreSQL 17.2 with native UUID support and JSONB columns
- **ORM**: SQLAlchemy Core with text() queries for optimal performance
- **Migrations**: Alembic handles database schema versioning and updates
- **Connection Pool**: SQLAlchemy engine with connection pooling for concurrent requests

---

## Slide 4: Prompts
### Database-Driven Prompt Management

**🗃️ Database Schema**
- **Table**: agent_prompts centralizes all prompt configurations in PostgreSQL
- **Versioning**: Integer version field with is_active boolean for prompt management
- **Flexibility**: JSONB metadata column stores additional prompt configuration data
- **Organization**: agent_id and prompt_type fields enable organized prompt categorization

**⚡ Runtime Retrieval**
- **Dynamic Loading**: Agents fetch prompts from database during runtime execution
- **Query Pattern**: ORDER BY version DESC LIMIT 1 ensures latest active prompt
- **Database Connection**: SQLAlchemy text() queries with parameterized inputs prevent injection
- **Caching**: Database connection pooling reduces prompt retrieval latency

**🔧 Implementation**
- **Database**: PostgreSQL stores all prompts with full ACID compliance
- **Query Engine**: SQLAlchemy text() provides raw SQL control for performance
- **Admin Interface**: FastAPI CRUD endpoints enable prompt management via API
- **Storage Format**: JSONB metadata enables flexible prompt configuration storage

---

## Slide 5: Analytics
### CloudWatch + Custom Metrics Pipeline

**📊 Cost Tracking Implementation**
- **Fixed Costs**: ALB routing ($0.000007), ECS processing ($0.000027), database operations
- **Variable Costs**: Bedrock inference varies by model - Claude 3.5 Sonnet vs Nova Lite
- **Per-Request Tracking**: Every API call calculates infrastructure and AI model costs
- **Cost Optimization**: Nova Lite fallback provides 75% cost reduction for simple queries

**📈 Monitoring Stack**
- **Metrics Collection**: Amazon CloudWatch receives custom metrics from application
- **Log Aggregation**: CloudWatch Logs captures structured JSON logs with trace correlation
- **Custom Dashboards**: Real-time visualization of API latency, token usage, and costs
- **Performance Tracking**: Request/response times, database query performance, model latency

**🔧 Implementation**
- **Environment**: AGNO_MONITOR=True enables telemetry collection in production
- **API Integration**: AGNO_API_KEY authenticates with monitoring service
- **Structured Logging**: JSON format enables efficient log parsing and analysis

---

## Slide 6: Observability
### OpenTelemetry + CloudWatch + Bedrock Guardrails

**🔍 Tracing Stack**
- **OpenTelemetry Setup**: TracerProvider with CloudWatchSpanExporter for distributed tracing
- **Span Processing**: BatchSpanProcessor efficiently batches trace data for CloudWatch
- **Context Propagation**: Trace context follows requests across agent handoffs and database calls
- **Performance Profiling**: Detailed timing data identifies bottlenecks in request processing

**📋 CloudWatch Metrics**
- **ECS Metrics**: Container CPU, memory utilization, and task count monitoring
- **RDS Metrics**: Database connections, read/write latency, and performance insights
- **ALB Metrics**: Request count, response times, and HTTP status code tracking
- **Bedrock Metrics**: Model invocations, input/output token counts, and error rates

**🛡️ Bedrock Guardrails**
- **Content Filtering**: Automatic detection and blocking of harmful content ($0.15 per 1K text units)
- **PII Detection**: Identifies and redacts personally identifiable information
- **Topic Filtering**: Prevents conversations on restricted or inappropriate topics
- **Contextual Grounding**: Ensures AI responses are factually accurate and sourced

**🔧 Technology Stack**
- **Tracing**: OpenTelemetry SDK with automatic instrumentation for FastAPI and SQLAlchemy
- **Monitoring**: Amazon CloudWatch provides centralized metrics and alerting
- **Logging**: Structured JSON logs with correlation IDs for request tracking
- **Alerting**: CloudWatch Alarms with SNS notifications for critical system events

---

## Slide 7: Intelligent Integration Agent
### Tool Framework + API Connectors

**🛠️ Tool Implementation**
- **DuckDuckGo Integration**: Web search tool provides real-time internet information access
- **Tool Framework**: Agno tool system enables dynamic tool selection and execution
- **Extensible Design**: Additional tools for database queries, API integration, file processing
- **Execution Control**: show_tool_calls=True provides transparency in tool usage

**🔧 Framework Details**
- **Tool System**: Agno framework handles tool registration, validation, and execution
- **Web Search**: DuckDuckGo Search API provides ad-free, privacy-focused web results
- **HTTP Client**: Built-in aiohttp/requests integration for API connectivity
- **Authentication**: Environment variable management for API keys and credentials
- **Error Handling**: Comprehensive retry logic, timeout configuration, and graceful failures

**📡 API Integration Pattern**
- **Custom Tools**: Template for building company-specific backend integrations
- **Authentication**: Bearer token, API key, and OAuth2 support for enterprise APIs
- **Async Processing**: Non-blocking API calls prevent request timeouts
- **Response Handling**: JSON parsing with error handling and data validation

---

## Slide 8: Knowledge
### S3 + PgVector + Embedding Pipeline

**📚 Knowledge Base Schema**
- **Vector Storage**: PostgreSQL with PgVector extension stores 1536-dimensional embeddings
- **Document Tracking**: document_name and chunk_index enable source attribution
- **Content Storage**: Full text content alongside embeddings for context retrieval
- **Metadata**: JSONB field stores document metadata, processing timestamps, and source info

**🗂️ Processing Pipeline**
- **Knowledge Implementation**: AgentKnowledge with PgVector backend for hybrid search
- **Search Strategy**: SearchType.hybrid combines semantic vector similarity with keyword matching
- **Database Integration**: Direct PostgreSQL connection with optimized vector operations
- **Performance**: IVFFlat index with vector_cosine_ops for fast similarity searches

**🔧 Technology Stack**
- **File Storage**: AWS S3 provides scalable document storage with versioning
- **Vector Database**: PostgreSQL 17.2 with PgVector extension for vector operations
- **Embeddings**: OpenAI text-embedding-3-small generates 1536-dimensional vectors
- **Search Optimization**: Hybrid approach combines semantic understanding with exact keyword matching
- **Processing**: Automated document chunking, embedding generation, and index maintenance

**📊 S3 Integration**
- **Bucket Configuration**: Private ACL with skip_delete protection for data safety
- **Upload Pipeline**: Admin portal uploads → S3 storage → processing queue → vector database
- **Access Control**: IAM policies restrict S3 access to authorized application components

---

## Slide 9: Config & Prompts
### ECS Fargate + Infrastructure as Code

**🏗️ ECS Configuration**
- **Container Orchestration**: FastAPI application runs on ECS Fargate with 1 vCPU and 2GB RAM
- **Command Execution**: Uvicorn serves FastAPI app with 2 workers for concurrent request handling
- **Health Monitoring**: Health check endpoint at /v1/health ensures container availability
- **Auto Scaling**: ECS service can scale based on CPU/memory utilization or request volume

**💾 Database Infrastructure**
- **RDS PostgreSQL**: Version 17.2 running on db.t4g.small instance class
- **Storage**: 64GB allocated storage with auto-scaling for growth
- **Performance**: Performance Insights enabled for query optimization and monitoring
- **Accessibility**: Publicly accessible for development, VPC-secured for production

**🔐 Security Groups**
- **Network Segmentation**: ALB → App (port 8000) → Database (port 5432) traffic flow
- **Ingress Rules**: Application Load Balancer security group allows internet access
- **Database Security**: Database security group only accepts connections from application tier
- **Principle of Least Privilege**: Each security group allows only necessary ports and sources

**🔧 Technology Stack**
- **Container Platform**: Amazon ECS Fargate provides serverless container execution
- **Load Balancing**: Application Load Balancer distributes traffic across healthy containers
- **Database**: Amazon RDS PostgreSQL with automated backups and maintenance
- **Infrastructure as Code**: Python-based configuration with Agno framework deployment tools
- **Secrets Management**: AWS Secrets Manager stores database credentials and API keys
- **Monitoring Integration**: CloudWatch logs and metrics collection enabled by default

---

## Final Slide: Technical Stack Summary
### Complete Technology Architecture

**🏗️ Core Technologies**
- **Runtime**: Python 3.11+ with async/await support for high-performance web services
- **Web Framework**: FastAPI provides automatic API documentation, validation, and async support
- **AI Framework**: Agno v1.4.6 handles agent lifecycle, memory, storage, and tool integration
- **AI Models**: Claude 3.5 Sonnet primary, Amazon Nova Lite fallback via Bedrock service
- **Database**: PostgreSQL 17.2 with PgVector extension for vector similarity search
- **Container Runtime**: Docker containers running on ECS Fargate serverless compute

**☁️ AWS Services**
- **Compute**: ECS Fargate provides 1 vCPU, 2GB RAM containers with automatic scaling
- **Database**: RDS PostgreSQL on db.t4g.small with Performance Insights and automated backups
- **Object Storage**: S3 for document uploads with private ACL and lifecycle policies
- **AI Services**: Amazon Bedrock for Claude 3.5 Sonnet and Nova Lite model access
- **Load Balancing**: Application Load Balancer with health checks and SSL termination
- **Observability**: CloudWatch for metrics, logs, and alarms with OpenTelemetry integration
- **Security**: IAM roles, VPC networking, Security Groups, and Secrets Manager

**📊 Data Flow**
- **Request Path**: Internet → ALB (port 80) → ECS (port 8000) → PostgreSQL (port 5432)
- **Monitoring**: CloudWatch collects metrics, OpenTelemetry provides distributed tracing
- **AI Processing**: Bedrock API calls for model inference with token usage tracking
- **Knowledge Retrieval**: PgVector similarity search with S3 document storage backend

**💰 Infrastructure Costs**
- **Monthly Operating Cost**: ~$60 total ($25 RDS + $15 ECS + $16 ALB + $4 ancillary services)
- **Per-Request Cost**: ~$0.0019 including infrastructure and Bedrock inference costs  
- **Scaling Economics**: Linear cost scaling via ECS service count adjustment 