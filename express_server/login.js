const express = require('express');
const mongoose = require('mongoose');
const passport = require('passport');
const bodyParser = require('body-parser');
const cors = require('cors');
const session = require('express-session');

const authRoutes = require('./routes/loginroutes/authRoutes');
const formRoutes = require('./routes/loginroutes/formRoutes');
const loginRoutes = require('./routes/loginroutes/loginRoutes');
require('./config/passportConfig');

const app = express();

app.use(cors({ credentials: true, origin: 'http://localhost:3000' }));
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

const corsOptions = {
  origin: 'http://localhost:3000', // Your front-end origin
  credentials: true, // Allow cookies and credentials
};

// Enable CORS for all routes
app.use(cors(corsOptions));

// Explicitly handle OPTIONS requests for preflight
app.options('*', cors(corsOptions)); // Handle preflight requests
app.use(
  session({
    secret: 'mycookiesaremycookiesnotyourcookiesbecausethesecookiesshallbemycookiesonly',
    resave: false,
    saveUninitialized: false,
  })
);

app.use(passport.initialize());
app.use(passport.session());

const mongoDBUrl = process.env.MONGODB_URL;

mongoose
  .connect(mongoDBUrl, {
    useNewUrlParser: true,
    useUnifiedTopology: true,
  })
  .then(() => console.log('Connected to MongoDB'))
  .catch((err) => console.error('MongoDB connection error:', err));

app.use('/auth', authRoutes);
app.use('/form', formRoutes);
app.use('/log', loginRoutes);

const PORT = 5000;
app.listen(PORT, () => console.log(`Server running on http://localhost:${PORT}`));
