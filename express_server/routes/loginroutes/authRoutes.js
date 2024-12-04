const express = require('express');
const passport = require('passport');
const otpGenerator = require('otp-generator');
const nodemailer = require('nodemailer');
const router = express.Router();
require('dotenv').config();
const otpStore = require('./otpstore');
const { getDynamicUserModel } = require('./utils'); // Import helper function

// Nodemailer configuration
const transporter = nodemailer.createTransport({
  service: 'gmail',
  auth: {
    user: process.env.EMAIL_USER,
    pass: process.env.EMAIL_PASS,
  },
});

// Google login route
router.get('/google', passport.authenticate('google', { scope: ['profile', 'email'] }));

// Google OAuth callback route
router.get(
  '/google/callback',
  passport.authenticate('google', { failureRedirect: 'http://localhost:3000' }),
  async (req, res) => {
    const userEmail = req.user.email;
    const userName = req.user.name;

    // Sanitize username
    const sanitizedUsername = userName.replace(/\s+/g, '_').toLowerCase();

    try {
      const UserCollection = getDynamicUserModel(sanitizedUsername);

      // Check if the user already exists
      const userData = await UserCollection.findOne({ 'formInfo.email': userEmail });

      if (userData) {
        // Redirect to their profile page
        return res.redirect(`http://localhost:3000/profile3?name=${encodeURIComponent(userName)}`);
      } else {
        // Generate OTP
        const otp = otpGenerator.generate(6, { digits: true, alphabets: false, specialChars: false });
        otpStore[userEmail] = otp;

        const mailOptions = {
          from: process.env.EMAIL_USER,
          to: userEmail,
          subject: 'Your OTP for Verification',
          text: `Your OTP is: ${otp}`,
        };

        transporter.sendMail(mailOptions, (err) => {
          if (err) {
            console.error('Error sending OTP:', err);
            return res.status(500).json({ error: 'Failed to send OTP.' });
          }

          // Redirect to the form page
          res.redirect(`http://localhost:3000/form?name=${encodeURIComponent(userName)}&email=${encodeURIComponent(userEmail)}`);
        });
      }
    } catch (err) {
      console.error('Error querying user collection:', err);
      return res.status(500).json({ error: 'Internal Server Error' });
    }
  }
);

// OTP verification route
router.post('/verify-otp', (req, res) => {
  const { email, otp } = req.body;

  if (otpStore[email] === otp) {
    delete otpStore[email]; // Remove OTP after successful verification
    res.status(200).json({ message: 'OTP verified successfully!' });
  } else {
    res.status(400).json({ error: 'Invalid OTP.' });
  }
});

// Logout route
router.get('/logout', (req, res) => {
  req.logout((err) => {
    if (err) {
      return res.status(500).json({ error: 'Failed to logout' });
    }
    res.redirect('http://localhost:3000');
  });
});

module.exports = router;
