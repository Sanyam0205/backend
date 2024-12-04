const express = require('express');
const User = require('../../models/userModel');
const router = express.Router();

router.post('/save', async (req, res) => {
  try {
    const { username, title, content } = req.body;

    if (!username || !title || !content) {
      return res.status(400).send('All fields are required');
    }

    const UserCollection = mongoose.model(username, User.schema, username);

    // Append a new document to the user's documents array
    await UserCollection.findOneAndUpdate(
      {},
      { $push: { documents: { title, content } } },
      { new: true }
    );

    res.status(200).send('Document saved successfully');
  } catch (error) {
    console.error('Error saving document:', error);
    res.status(500).send('Internal Server Error');
  }
});

module.exports = router;
