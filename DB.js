const mysql = require('mysql')
const util = require('util')
require('dotenv').config()

const pool = mysql.createPool({
    connectionLimit: 10,
    host: process.env.MYSQL_HOST || 'localhost',
    database: process.env.MYSQL_DATABASE || 'mazes_db',
    user: process.env.MYSQL_USER || 'admin',
    password: process.env.MYSQL_PASSWORD || '321nimda',
    timezone: 'UTC'
})

const getConnection = util.promisify(pool.getConnection).bind(pool);
const query = util.promisify(pool.query).bind(pool);

const connectDB = async () => {
    let retries = 5;
    let res;
    while(retries > 0){
        try{
            res = await getConnection();
            console.log('--------mysql pool connected-------------');
            res.release()
            break;
        }catch(e){
            retries--;
            console.log(e.message, `, Retries remaining: ${retries}`);
            await new Promise(resolve => setTimeout(resolve,5000))
        }
    }
    if(retries===0) console.log('Unable to connect to mysql');
    
}

connectDB();

module.exports = {
    pool:pool,
    getConnection:getConnection,
    query:query
}