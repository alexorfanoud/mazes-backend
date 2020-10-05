const { AuthError } = require('../../errors/models')
const jwt = require('jsonwebtoken')
const {query} = require('../../DB')
require('dotenv').config();

const userRoute = async (req,res,next) => {

    const token = req.headers['authorisation'];    
    try{
        if(!token) { 
            throw new AuthError({token: 'No token provided'}); 
        }
        const expired = await query('SELECT 1 FROM expired_tokens WHERE token=? LIMIT 1',[token]);
        if(!!expired[0]){
            throw new AuthError({token: 'Token is expired'})
        }
        try {
            jwt.verify(token, process.env.TOKEN_SECRET)
        }catch(e){
            throw new AuthError({token:'Invalid Token'})
        }
        next();
    }
    catch(e){
        res.status(e.status).send(e.info)
    }
    
}

module.exports = {
    userRoute:userRoute
}