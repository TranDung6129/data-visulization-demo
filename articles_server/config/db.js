const mongoose = require('mongoose');

async function connectDb() {
    try {
        await mongoose.connect('mongodb://mongo:27017/big-data');
        console.log('Connect successfully!!!');
    } catch (error) {
        console.log('Connect fail!!!');
    }
}
module.exports = { connectDb };




