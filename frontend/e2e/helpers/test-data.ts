/**
 * Test data helpers for E2E tests
 */

export const testUsers = {
  valid: {
    firstName: 'John',
    lastName: 'Doe',
    username: 'johndoe',
    email: 'john@example.com',
    password: 'password123',
  },
  invalid: {
    email: 'invalid-email',
    shortPassword: 'short',
    mismatchedPassword: 'different123',
  },
  existing: {
    email: 'existing@example.com',
    username: 'existinguser',
  },
};

export const mockTokens = {
  access: 'mock-access-token',
  refresh: 'mock-refresh-token',
  expired: 'expired-token',
};

export const mockUserData = {
  valid: {
    id: 'user-123',
    email: 'john@example.com',
    username: 'johndoe',
    first_name: 'John',
    last_name: 'Doe',
    full_name: 'John Doe',
    is_active: true,
    is_verified: true,
    totp_enabled: false,
    timezone: 'UTC',
    language: 'en',
    last_login: '2024-01-01T00:00:00Z',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
};

export const apiResponses = {
  successfulLogin: {
    status: 200,
    body: {
      access_token: mockTokens.access,
      refresh_token: mockTokens.refresh,
      expires_in: 1800,
      refresh_expires_in: 604800,
    },
  },
  successfulRegistration: {
    status: 201,
    body: {
      access_token: mockTokens.access,
      refresh_token: mockTokens.refresh,
      expires_in: 1800,
      refresh_expires_in: 604800,
    },
  },
  invalidCredentials: {
    status: 401,
    body: {
      detail: 'Invalid credentials',
    },
  },
  duplicateEmail: {
    status: 400,
    body: {
      detail: 'Email already registered',
    },
  },
  duplicateUsername: {
    status: 400,
    body: {
      detail: 'Username already taken',
    },
  },
  tokenExpired: {
    status: 401,
    body: {
      detail: 'Token expired',
    },
  },
  serverError: {
    status: 500,
    body: {
      detail: 'Internal server error',
    },
  },
};
