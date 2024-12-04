const express = require('express');
const bcrypt = require('bcrypt');
const otpStore = require('./otpstore');
const { getDynamicUserModel } = require('./utils');
const mongoose = require('mongoose');

const router = express.Router();

const usersSchema = new mongoose.Schema(
  {
    email: { type: String, required: true, unique: true },
    username: { type: String, required: true },
    password: { type: String },
    scopusId: { type: String },
  },
  { timestamps: true }
);
const Users = mongoose.models.Users || mongoose.model('Users', usersSchema, 'users');

router.post('/', async (req, res) => {
  try {
    console.log('Form data:', req.body);
    const { name, email, scopusId, otp } = req.body;

    if (!name || !email || !scopusId || !otp) {
      return res.status(400).json({ error: 'All fields including OTP are required.' });
    }

    console.log('OTP store:', otpStore);

    // Validate OTP
    if (
      (typeof otpStore[email] === 'object' && otp !== otpStore[email]?.otp) ||
      (typeof otpStore[email] === 'string' && otp !== otpStore[email])
    ) {
      return res.status(400).json({ success: false, message: 'Invalid OTP' });
    }

    const password = otpStore[email]?.password || null; // Use null if no password
    const sanitizedUsername = name.replace(/\s+/g, '_').toLowerCase();

    // Hash the password if it exists
    const hashedPassword = password ? await bcrypt.hash(password, 10) : null;

    // Save the user details in the 'users' collection
    const existingUser = await Users.findOne({ email });
    if (!existingUser) {
      await Users.create({
        email,
        username: sanitizedUsername,
        password: hashedPassword,
        scopusId,
      });
    }

    // Remove OTP entry after successful validation
    delete otpStore[email];

    // Save data in a separate dynamic user collection
    const UserCollection = getDynamicUserModel(sanitizedUsername);
    await UserCollection.findOneAndUpdate(
      { 'formInfo.email': email },
      { $set: { formInfo: { name, email, scopusId } } },
      { upsert: true, new: true }
    );

    res.json({ name: sanitizedUsername });
  } catch (error) {
    console.error('Error saving form data:', error);
    res.status(500).json({ error: 'Internal Server Error' });
  }
});

module.exports = router;
