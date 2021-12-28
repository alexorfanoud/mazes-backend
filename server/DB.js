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
    while(1){
        try{
            res = await getConnection();
            console.log('--------mysql pool connected-------------');
            res.release()
            break;
        }catch(e){
            console.log(e.message);
            await new Promise(resolve => setTimeout(resolve,5000))
        }
    }
}

connectDB();

module.exports = {
    pool:pool,
    getConnection:getConnection,
    query:query
}
