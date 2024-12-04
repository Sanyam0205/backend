const express = require('express');
const mongoose = require('mongoose');
const passport = require('passport');
const bodyParser = require('body-parser');
const session = require('express-session');

const authRoutes = require('./routes/loginroutes/authRoutes');
const formRoutes = require('./routes/loginroutes/formRoutes');
const loginRoutes = require('./routes/loginroutes/loginRoutes');
require('./config/passportConfig');

const app = express();

// Middleware for parsing JSON and URL-encoded data
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// CORS middleware
const allowCors = (fn) => async (req, res) => {
  res.setHeader('Access-Control-Allow-Credentials', true);
  res.setHeader('Access-Control-Allow-Origin', 'http://localhost:3000'); // Front-end origin
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,PATCH,DELETE,POST,PUT');
  res.setHeader(
    'Access-Control-Allow-Headers',
    'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version, Authorization'
  );
  if (req.method === 'OPTIONS') {
    res.status(200).end(); // Handle preflight requests
    return;
  }
  return await fn(req, res);
};

// Apply `allowCors` to a dummy handler for global CORS handling
const globalCorsHandler = allowCors((req, res) => res.next());
app.use(globalCorsHandler);

// Session configuration
app.use(
  session({
    secret: 'mycookiesaremycookiesnotyourcookiesbecausethesecookiesshallbemycookiesonly',
    resave: false,
    saveUninitialized: false,
  })
);

// Passport initialization
app.use(passport.initialize());
app.use(passport.session());

// MongoDB connection
const mongoDBUrl = process.env.MONGODB_URL;

mongoose
  .connect(mongoDBUrl, {
    useNewUrlParser: true,
    useUnifiedTopology: true,
  })
  .then(() => console.log('Connected to MongoDB'))
  .catch((err) => console.error('MongoDB connection error:', err));

// Route handlers
app.use('/auth', allowCors(authRoutes));
app.use('/form', allowCors(formRoutes));
app.use('/log', allowCors(loginRoutes));

// Start server
const PORT = 5000;
app.listen(PORT, () => console.log(`Server running on http://localhost:${PORT}`));
