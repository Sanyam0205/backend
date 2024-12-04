const express = require('express');
const router = express.Router();

// Define the POST route
router.post('/profiles', async (req, res) => {
    try {
        console.log("Received data:", JSON.stringify(req.body, null, 2));  // Print full data for debugging
        const db = req.app.locals.db;  // Use MongoDB client provided by server.js
        const collection = db.collection("profiles");

        // Extract data from the request body
        const { author, masterdata, short_publications, interests, summary, master_all_data } = req.body;

        // Explicitly specify payload structure before inserting into MongoDB
        const payload = {
            author,
            masterdata,
            short_publications,
            interests: interests.interests,  // Ensure interests field is an array
            summary,
            master_all_data  // Include the summary field
        };

        // Log the payload for final inspection before inserting
        console.log("Payload being inserted:", JSON.stringify(payload, null, 2));

        // Insert the payload into MongoDB
        const result = await collection.insertOne(payload);

        if (result.insertedId) {
            res.status(201).send({ message: 'Data successfully saved to MongoDB', result });
        } else {
            res.status(400).send({ message: 'Failed to insert data' });
        }
    } catch (error) {
        console.error("Failed to insert data into MongoDB:", error);
        res.status(500).send({ error: "Failed to save data to MongoDB" });
    }
});

module.exports = router;
