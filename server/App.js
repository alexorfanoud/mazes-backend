const express = require('express')
const bodyParser = require('body-parser')
const cors = require('cors')
require('dotenv').config()

const PORT = !!process.env.SERVER_PORT ? process.env.SERVER_PORT : 3001;

const app = express();
app.listen(PORT, ()=> console.log(`Server listening on port ${PORT}`))

app.use(cors())
app.use(bodyParser.json())
app.use(bodyParser.urlencoded({extended:true, limit: '50mb'}))

app.get('/', (req,res)=>{
    res.send('WELCOME')
})

app.use('/auth', require('./routes/auth'))
app.use('/healthcheck', require('./routes/healthcheck'))
app.use('/mazes', require('./middlewares/user/auth').userRoute, require('./routes/mazes'))


module.exports = app;
 
     







        
