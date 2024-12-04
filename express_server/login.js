const express = require('express');
const mongoose = require('mongoose');
const passport = require('passport');
const bodyParser = require('body-parser');
const session = require('express-session');
const cors = require('cors');
const authRoutes = require('./routes/loginroutes/authRoutes');
const formRoutes = require('./routes/loginroutes/formRoutes');
const loginRoutes = require('./routes/loginroutes/loginRoutes');
require('./config/passportConfig');

const app = express();

// Middleware for parsing JSON and URL-encoded data
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// CORS middleware
app.use(cors({
  origin: process.env.FRONTEND_URL || 'http://localhost:3000',
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['X-CSRF-Token', 'X-Requested-With', 'Accept', 'Accept-Version', 'Content-Length', 'Content-MD5', 'Content-Type', 'Date', 'X-Api-Version', 'Authorization']
}));

// Session configuration
app.use(session({
  secret: 'mycookiesaremycookiesnotyourcookiesbecausethesecookiesshallbemycookiesonly',
  resave: false,
  saveUninitialized: false,
}));

// Passport initialization
app.use(passport.initialize());
app.use(passport.session());

// MongoDB connection
const mongoDBUrl = process.env.MONGODB_URL;
mongoose.connect(mongoDBUrl, { useNewUrlParser: true, useUnifiedTopology: true })
  .then(() => console.log('Connected to MongoDB'))
  .catch((err) => console.error('MongoDB connection error:', err));

// Route handlers
app.use('/auth', authRoutes);
app.use('/form', formRoutes);
app.use('/log', loginRoutes);

// Start server
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`Server running on http://localhost:${PORT}`));