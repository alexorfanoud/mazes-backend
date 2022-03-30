const { query } = require('../../DB.js')
const bcrypt = require('bcrypt')
const jwt = require('jsonwebtoken')
const { AuthError, BadRequest } = require('../../errors/models')
require('dotenv').config()

require('dotenv').config()

const signup = async (userOpts) => {

    try{
        const salt = await bcrypt.genSalt(10);
        const hash = await bcrypt.hash(userOpts.password, salt)
        const result = await query(`INSERT INTO user (email,password) VALUES (?,?)`,[userOpts.email,hash])
        const token = jwt.sign({_id:result.insertId}, process.env.TOKEN_SECRET)
        return {email:userOpts.email, token: token}
    }catch(e){
        throw new BadRequest({global:'User already exists'});
    }
    
}

const login = async (userOpts) => {
    
        const user = await query(`SELECT Id,password FROM user WHERE email=? LIMIT 1`,[userOpts.email]);
        if(!user[0]) throw new BadRequest({email: 'Wrong email'});
        const userPassword = user[0].password;       
        const validates = await bcrypt.compare(userOpts.password, userPassword);
        if(!validates) throw new AuthError({password: 'Wrong password'});
        const token = await jwt.sign({_id:user[0].Id}, process.env.TOKEN_SECRET, {expiresIn:'180m'})
        return {email:userOpts.email,token:token} 
}

const logout = async (token) => {
    
    await query(`INSERT INTO expired_tokens(token) VALUES (?)`,[token]);
    return {status:'Loggout Succesful'} 

}

module.exports = {
    signup:signup,
    login:login,
    logout:logout
}
