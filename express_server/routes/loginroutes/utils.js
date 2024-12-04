const mongoose = require('mongoose');

// Reusable dynamic model helper for user collections
const getDynamicUserModel = (uniqueId) => {
  const userSchema = new mongoose.Schema(
    {
      formInfo: {
        email: { type: String, required: true },
        name: { type: String, required: true },
        scopusId: { type: String },
        additionalField1: { type: String },
        additionalField2: { type: String },
      },
      credentials: {
        password: { type: String, required: true },
      },
      documents: [
        {
          title: { type: String },
          content: { type: String },
          createdAt: { type: Date, default: Date.now },
        },
      ],
    },
    { strict: false }
  );

  return mongoose.models[uniqueId] || mongoose.model(uniqueId, userSchema, uniqueId);
};

module.exports = { getDynamicUserModel };
