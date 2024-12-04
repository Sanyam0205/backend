const express = require('express');
const bcrypt = require('bcrypt');
const otpGenerator = require('otp-generator');
const nodemailer = require('nodemailer');
const mongoose = require('mongoose');
const otpStore = require('./otpstore');
const { getDynamicUserModel } = require('./utils'); // Helper for user collections

const router = express.Router();

// Nodemailer configuration
if (!process.env.EMAIL_USER || !process.env.EMAIL_PASS) {
  throw new Error('Missing environment variables for email configuration');
}
const transporter = nodemailer.createTransport({
  service: 'gmail',
  auth: {
    user: process.env.EMAIL_USER,
    pass: process.env.EMAIL_PASS,
  },
});

// Users schema and model
const usersSchema = new mongoose.Schema(
  {
    email: { type: String, required: true, unique: true },
    username: { type: String, required: true },
    password: { type: String, required: true },
    scopusId: { type: String },
  },
  { timestamps: true }
);
const Users = mongoose.models.Users || mongoose.model('Users', usersSchema, 'users');

// Endpoint to send OTP
router.post('/send-otp', async (req, res) => {
  const { email, password, username } = req.body;

  if (!email || !password || !username) {
    return res.status(400).json({ success: false, message: 'Email, password, and username are required' });
  }

  try {
    const existingUser = await Users.findOne({ email });
    if (existingUser) {
      return res.status(400).json({ success: false, message: 'Email already registered' });
    }

    const otp = otpGenerator.generate(6, { digits: true, alphabets: false, specialChars: false });
    const otpExpiry = Date.now() + 10 * 60 * 1000; // OTP expires in 10 minutes
    otpStore[email] = { otp, password, username, expiry: otpExpiry };

    const mailOptions = {
      from: process.env.EMAIL_USER,
      to: email,
      subject: 'Your OTP for Signup Verification',
      text: `Your OTP is: ${otp}`,
    };

    transporter.sendMail(mailOptions, (err) => {
      if (err) {
        console.error('Error sending OTP:', err);
        return res.status(500).json({ success: false, message: 'Failed to send OTP' });
      }

      res.status(200).json({ success: true, message: 'OTP sent successfully', formRedirectUrl: `/form?email=${encodeURIComponent(email)}` });
    });
  } catch (error) {
    console.error('Error sending OTP:', error);
    res.status(500).json({ success: false, message: 'Server error' });
  }
});

// Endpoint to handle login (without JWT)
router.post('/login', async (req, res) => {
  const { email, password } = req.body;

  if (!email || !password) {
    return res.status(400).json({ success: false, message: 'Email and password are required' });
  }

  try {
    // Find the user by email
    const user = await Users.findOne({ email });

    if (!user) {
      return res.status(400).json({ success: false, message: 'Invalid email or password' });
    }

    // Compare the provided password with the stored hashed password
    const isMatch = await bcrypt.compare(password, user.password);

    if (!isMatch) {
      return res.status(400).json({ success: false, message: 'Invalid email or password' });
    }

    // Respond with success (no JWT)
    res.status(200).json({ success: true, message: 'Login successful' });

  } catch (error) {
    console.error('Error during login:', error);
    res.status(500).json({ success: false, message: 'Server error' });
  }
});

module.exports = router;
