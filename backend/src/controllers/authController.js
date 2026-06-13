const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const crypto = require('crypto');
const prisma = require('../config/prisma');

const generateAccessToken = (user) => {
  return jwt.sign(
    { user_id: user.user_id, email: user.email, role: user.role },
    process.env.JWT_SECRET,
    { expiresIn: '15m' }
  );
};

const generateRefreshToken = async (user) => {
  const token = crypto.randomBytes(40).toString('hex');
  const tokenHash = crypto.createHash('sha256').update(token).digest('hex');

  await prisma.refreshToken.create({
    data: {
      user_id: user.user_id,
      token_hash: tokenHash,
      expires_at: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000), // 7 days
    },
  });

  return token;
};

// POST /api/v1/auth/register
const register = async (req, res) => {
  try {
    const { email, password, first_name, last_name, role } = req.body;

    if (!email || !password || !first_name || !last_name || !role) {
      return res.status(400).json({ message: 'All fields are required' });
    }

    if (!['admin', 'analyst', 'executive'].includes(role)) {
      return res.status(400).json({ message: 'Invalid role' });
    }

    const existingUser = await prisma.user.findUnique({ where: { email } });
    if (existingUser) {
      return res.status(409).json({ message: 'Email already registered' });
    }

    const password_hash = await bcrypt.hash(password, 12);

    const user = await prisma.user.create({
      data: { email, password_hash, first_name, last_name, role },
      select: { user_id: true, email: true, first_name: true, last_name: true, role: true, created_at: true },
    });

    res.status(201).json({ status: 'success', data: user });
  } catch (error) {
    console.error('Register error:', error);
    res.status(500).json({ message: 'Internal server error' });
  }
};

// POST /api/v1/auth/login
const login = async (req, res) => {
  try {
    const { email, password } = req.body;

    if (!email || !password) {
      return res.status(400).json({ message: 'Email and password are required' });
    }

    const user = await prisma.user.findUnique({ where: { email } });
    if (!user) {
      return res.status(401).json({ message: 'Invalid credentials' });
    }

    if (!user.is_active) {
      return res.status(403).json({ message: 'Account is deactivated' });
    }

    const isValidPassword = await bcrypt.compare(password, user.password_hash);
    if (!isValidPassword) {
      return res.status(401).json({ message: 'Invalid credentials' });
    }

    const accessToken = generateAccessToken(user);
    const refreshToken = await generateRefreshToken(user);

    await prisma.user.update({
      where: { user_id: user.user_id },
      data: { last_login_at: new Date() },
    });

    res.json({
      status: 'success',
      data: {
        access_token: accessToken,
        refresh_token: refreshToken,
        user: {
          user_id: user.user_id,
          email: user.email,
          first_name: user.first_name,
          last_name: user.last_name,
          role: user.role,
        },
      },
    });
  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({ message: 'Internal server error' });
  }
};

// POST /api/v1/auth/refresh
const refresh = async (req, res) => {
  try {
    const { refresh_token } = req.body;
    if (!refresh_token) {
      return res.status(400).json({ message: 'Refresh token required' });
    }

    const tokenHash = crypto.createHash('sha256').update(refresh_token).digest('hex');
    const storedToken = await prisma.refreshToken.findUnique({
      where: { token_hash: tokenHash },
      include: { user: true },
    });

    if (!storedToken || storedToken.revoked || storedToken.expires_at < new Date()) {
      return res.status(403).json({ message: 'Invalid or expired refresh token' });
    }

    await prisma.refreshToken.update({
      where: { token_id: storedToken.token_id },
      data: { revoked: true },
    });

    const accessToken = generateAccessToken(storedToken.user);
    const newRefreshToken = await generateRefreshToken(storedToken.user);

    res.json({
      status: 'success',
      data: { access_token: accessToken, refresh_token: newRefreshToken },
    });
  } catch (error) {
    console.error('Refresh error:', error);
    res.status(500).json({ message: 'Internal server error' });
  }
};

// POST /api/v1/auth/logout
const logout = async (req, res) => {
  try {
    const { refresh_token } = req.body;
    if (refresh_token) {
      const tokenHash = crypto.createHash('sha256').update(refresh_token).digest('hex');
      await prisma.refreshToken.updateMany({
        where: { token_hash: tokenHash },
        data: { revoked: true },
      });
    }
    res.json({ status: 'success', message: 'Logged out successfully' });
  } catch (error) {
    console.error('Logout error:', error);
    res.status(500).json({ message: 'Internal server error' });
  }
};

module.exports = { register, login, refresh, logout };