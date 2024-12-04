// server.js
const express = require('express');
const { MongoClient } = require('mongodb');
const profileRoutes = require('./routes/profileRoutes'); 
const app = express();
app.use(express.json({ limit: '100mb' }));  
app.use(express.urlencoded({ extended: true, limit: '100mb' }));

const uri = "mongodb://localhost:27017"; 
const client = new MongoClient(uri);

async function main() {
    try {
        await client.connect();
        console.log("Connected to MongoDB");
        app.locals.db = client.db("mydatabase");  
        app.use('/api', profileRoutes);

        // Start the server
        app.listen(5000, () => {
            console.log('Server is running on http://localhost:5000');
        });
    } catch (error) {
        console.error("Failed to connect to MongoDB:", error);
    }
}
main();
