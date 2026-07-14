require('dotenv').config();
const request = require('supertest');
const express = require('express');
const cors = require('cors');
const authRoutes = require('../src/routes/authRoutes');

const app = express();
app.use(cors());
app.use(express.json());
app.use('/api/v1/auth', authRoutes);

describe('Auth API', () => {
  const testUser = {
    email: `test${Date.now()}@cirop.com`,
    password: 'Test@123',
    first_name: 'Test',
    last_name: 'User',
    role: 'analyst',
  };

  let accessToken = '';

  test('POST /api/v1/auth/register — should register new user', async () => {
    const res = await request(app).post('/api/v1/auth/register').send(testUser);
    expect(res.status).toBe(201);
    expect(res.body.status).toBe('success');
    expect(res.body.data.email).toBe(testUser.email);
  });

  test('POST /api/v1/auth/login — should login user', async () => {
    const res = await request(app).post('/api/v1/auth/login').send({
      email: testUser.email,
      password: testUser.password,
    });
    expect(res.status).toBe(200);
    expect(res.body.status).toBe('success');
    expect(res.body.data.access_token).toBeDefined();
    accessToken = res.body.data.access_token;
  });

  test('POST /api/v1/auth/register — should reject duplicate email', async () => {
    const res = await request(app).post('/api/v1/auth/register').send(testUser);
    expect(res.status).toBe(409);
  });

  test('POST /api/v1/auth/login — should reject wrong password', async () => {
    const res = await request(app).post('/api/v1/auth/login').send({
      email: testUser.email,
      password: 'wrongpassword',
    });
    expect(res.status).toBe(401);
  });
});