# API Specification

## Base URL
- **Development**: `http://localhost:8000`
- **Staging**: `https://api-staging.thetally.app`
- **Production**: `https://api.thetally.app`

## Authentication

### Human Users
All endpoints except `/health`, `/auth/register`, and `/auth/login` require authentication via JWT Bearer token.

```http
Authorization: Bearer <access_token>
```

### Automated Systems
API endpoints can be accessed using API keys for automated systems, AI assistants, and CI/CD pipelines.

```http
Authorization: Bearer <api_key>
X-API-Key: <api_key>
```

### Service Accounts
For CI/CD and automated deployments, use GCP service account tokens.

```http
Authorization: Bearer <service_account_token>
```

## API Endpoints

*This section will be populated as we develop the application*

### Health Check

#### GET /health
Returns the health status of the API.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "version": "1.0.0"
}
```

### Authentication

#### POST /auth/register
Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "full_name": "John Doe"
}
```

**Response:**
```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "John Doe",
    "is_active": true,
    "is_otp_enabled": false
  },
  "access_token": "jwt_token",
  "refresh_token": "refresh_jwt_token",
  "token_type": "bearer"
}
```

#### POST /auth/login
Authenticate user and return tokens.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "otp_code": "123456"  // Optional, required if 2FA enabled
}
```

**Response:**
```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "John Doe",
    "is_active": true,
    "is_otp_enabled": true
  },
  "access_token": "jwt_token",
  "refresh_token": "refresh_jwt_token",
  "token_type": "bearer"
}
```

#### POST /auth/refresh
Refresh access token using refresh token.

**Request Body:**
```json
{
  "refresh_token": "refresh_jwt_token"
}
```

**Response:**
```json
{
  "access_token": "new_jwt_token",
  "token_type": "bearer"
}
```

### API Key Management

#### POST /auth/api-keys
Create a new API key for automated access.

**Headers:** `Authorization: Bearer <jwt_token>`

**Request Body:**
```json
{
  "name": "AI Assistant Key",
  "permissions": ["read:transactions", "write:imports"],
  "expires_in_days": 365
}
```

**Response:**
```json
{
  "api_key": "ak_1234567890abcdef",
  "name": "AI Assistant Key",
  "permissions": ["read:transactions", "write:imports"],
  "expires_at": "2024-12-31T23:59:59Z",
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### GET /auth/api-keys
List all API keys for the current user.

**Headers:** `Authorization: Bearer <jwt_token>`

**Response:**
```json
[
  {
    "id": "uuid",
    "name": "AI Assistant Key",
    "permissions": ["read:transactions", "write:imports"],
    "expires_at": "2024-12-31T23:59:59Z",
    "created_at": "2024-01-01T00:00:00Z",
    "last_used": "2024-01-15T10:30:00Z"
  }
]
```

#### DELETE /auth/api-keys/{key_id}
Revoke an API key.

**Headers:** `Authorization: Bearer <jwt_token>`

**Response:**
```json
{
  "message": "API key revoked successfully"
}
```

### User Management

#### GET /users/me
Get current user profile.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "is_otp_enabled": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### File Import

#### POST /import/upload
Upload and process financial data files.

**Headers:** `Authorization: Bearer <token>`

**Request Body:** `multipart/form-data`
- `file`: CSV/OFX/QIF file
- `account_id`: UUID of the account to import into

**Response:**
```json
{
  "import_id": "uuid",
  "status": "processing",
  "total_transactions": 150,
  "processed_transactions": 0,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Transactions

#### GET /transactions
List user transactions with filtering and pagination.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 50, max: 100)
- `account_id`: Filter by account
- `category_id`: Filter by category
- `start_date`: Filter from date (ISO 8601)
- `end_date`: Filter to date (ISO 8601)
- `search`: Search in description

**Response:**
```json
{
  "transactions": [
    {
      "id": "uuid",
      "account_id": "uuid",
      "amount": -25.50,
      "description": "Tesco Supermarket",
      "date": "2024-01-01",
      "category": {
        "id": "uuid",
        "name": "Groceries",
        "color": "#FF5722"
      },
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 50,
    "total": 150,
    "pages": 3
  }
}
```

### Categories

#### GET /categories
List all user categories.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
[
  {
    "id": "uuid",
    "name": "Groceries",
    "color": "#FF5722",
    "icon": "shopping_cart",
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

#### POST /categories
Create a new category.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "name": "Groceries",
  "color": "#FF5722",
  "icon": "shopping_cart"
}
```

### Categorization Rules

#### GET /rules
List all categorization rules.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
[
  {
    "id": "uuid",
    "pattern": "Tesco",
    "category_id": "uuid",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

#### POST /rules
Create a new categorization rule.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "pattern": "Tesco",
  "category_id": "uuid",
  "is_active": true
}
```

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Error message",
  "error_code": "ERROR_CODE",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Common Error Codes
- `VALIDATION_ERROR` - Request validation failed
- `UNAUTHORIZED` - Authentication required
- `FORBIDDEN` - Insufficient permissions
- `NOT_FOUND` - Resource not found
- `CONFLICT` - Resource already exists
- `INTERNAL_ERROR` - Server error

## Rate Limiting

- **Authentication endpoints**: 5 requests per minute
- **General API**: 100 requests per minute per user
- **File upload**: 10 requests per hour per user

---

*This specification will be updated as we develop the API endpoints.*
