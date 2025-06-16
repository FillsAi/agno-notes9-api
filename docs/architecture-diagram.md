# 2. AWS Architecture Diagram 🏗️

## 2.1 Your Complete AI Agent API Infrastructure

```
                                    🌐 Internet
                                         |
                                         |
                     ┌─────────────────────────────────────┐
                     │      Application Load Balancer      │
                     │     (agent-api-prd-api-lb)          │
                     │    Port 80/443 → Port 8000          │
                     │   DNS: agent-api-prd-api-lb-        │
                     │    1166124937.us-east-1.elb.aws...  │
                     └─────────────────┬───────────────────┘
                                       |
                    ┌──────────────────┼──────────────────┐
                    │    Target Group  │                  │
                    │  (agent-api-prd-api-tg)             │
                    │    Health Check: /v1/health         │
                    └──────────────────┬──────────────────┘
                                       |
                     ┌─────────────────┴───────────────────┐
                     │          ECS Cluster                │
                     │     (agent-api-prd-cluster)         │
                     │                                     │
                     │   ┌─────────────────────────────┐   │
                     │   │     ECS Service             │   │
                     │   │ (agent-api-prd-api-service) │   │
                     │   │                             │   │
                     │   │  ┌─────────────────────┐    │   │
                     │   │  │   ECS Task          │    │   │
                     │   │  │ (FastAPI Container) │    │   │
                     │   │  │                     │    │   │
                     │   │  │ CPU: 1024 (1 vCPU)  │    │   │
                     │   │  │ Memory: 2048 MB     │    │   │
                     │   │  │ Workers: 2          │    │   │
                     │   │  │ Port: 8000          │    │   │
                     │   │  └─────────────────────┘    │   │
                     │   └─────────────────────────────┘   │
                     └─────────────────┬───────────────────┘
                                       |
                                       | Database Connection
                                       | Port 5432
                                       |
                     ┌─────────────────┴───────────────────┐
                     │         RDS Database                │
                     │     (agent-api-prd-db)              │
                     │                                     │
                     │  Engine: PostgreSQL 17.2            │
                     │  Instance: db.t4g.small             │
                     │  Storage: 64GB                      │
                     │  Database: ai                       │
                     │  Port: 5432                         │
                     └─────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                        Security Groups                          │
├─────────────────────────────────────────────────────────────────┤
│     agent-api-prd-lb-sg:                                        │
│     - Allows: Internet → Load Balancer (Port 80/443)            │
│                                                                 │
│      agent-api-prd-sg:                                          │
│       - Allows: Load Balancer → App (Port 8000)                 │
│                                                                 │
│      agent-api-prd-db-sg:                                       │
│       - Allows: App → Database (Port 5432)                      │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                       Secrets Manager                           │
├─────────────────────────────────────────────────────────────────┤
│     agent-api-prd-secrets:                                      │
│      - SECRET_KEY, APP_PASSWORD, OPENAI_API_KEY                 │
│                                                                 │
│     agent-api-prd-db-secrets:                                   │
│      - MASTER_USERNAME: agno                                    │
│       - MASTER_USER_PASSWORD: agno9999!!                        │
└─────────────────────────────────────────────────────────────────┘
```

## 2.2 Network Details

### 2.2.1 Subnets Used:
- `subnet-0737407494d0bece0` (us-east-1a)
- `subnet-0cf76bae1f89ad68e` (us-east-1b)

### 2.2.2 VPC:
- `vpc-0c47fe79175922265`

### 2.2.3 Region:
- `us-east-1` (N. Virginia)

## 2.3 IAM Roles Created:

### 2.3.1 Task Execution Role:
- `agent-api-prd-api-td-execution-role`
- Policies:
  - AmazonECSTaskExecutionRolePolicy
  - CloudWatchFullAccess
  - Custom ECS Secret Policy

### 2.3.2 Task Role:
- `agent-api-prd-api-td-task-role`
- Policies:
  - AmazonECSTaskExecutionRolePolicy
  - CloudWatchFullAccess
  - SecretsManagerReadWrite
  - AmazonS3FullAccess
  - Custom Bedrock Access Policy

## 2.4 Request Flow:

```
1. 🌐 User Request → Load Balancer (HTTP/HTTPS)
2. ⚖️ Load Balancer → Target Group → ECS Task (Port 8000)
3. 🐳 ECS Task → Processes Request (FastAPI + 2 Workers)
4. 🗃️ ECS Task → Database Query (PostgreSQL)
5. 📤 Database → ECS Task → Load Balancer → User
```

## 2.5 Cost Per Hour:

```
💰 RDS (db.t4g.small):      $0.034/hour  (~$25/month)
💰 ECS Fargate (1vCPU,2GB): $0.020/hour  (~$15/month)
💰 Load Balancer:           $0.022/hour  (~$16/month)
💰 Secrets Manager:         $0.040/month (~$1/month)
────────────────────────────────────────────────────
💰 Total:                   $0.076/hour  (~$57/month)
```

Your infrastructure is now live and running! 🚀 