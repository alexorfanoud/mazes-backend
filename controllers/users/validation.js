const  validator = require('validator')
const { BadRequest } = require('../../errors/models')

const signup = (userOpts) => {
    let errors = {};
    if(Object.keys(userOpts).length === 0) throw new BadRequest({global:'Credentials not provided'});
    if(!userOpts.email || validator.isEmpty(userOpts.email) ) errors.email = 'Email not provided'
    if( userOpts.email && !validator.isEmail(userOpts.email) ) errors.email = 'Invalid Email';
    if(!userOpts.password || validator.isEmpty(userOpts.password) ) errors.password = 'Password not provided'
    if(!userOpts.passConfirmation || validator.isEmpty(userOpts.passConfirmation) ) errors.passConfirmation = 'Password confirmation not provided'
    if( userOpts.password && userOpts.passConfirmation && !validator.equals(userOpts.password,userOpts.passConfirmation) ) errors.passConfirmation = 'Passwords dont match'

    if(!!Object.keys(errors).length)  throw new BadRequest(errors)//throw new Error(JSON.stringify(errors))
    else return true;
}

const login = (userOpts) => {
    let errors = {};
    if(Object.keys(userOpts).length === 0) throw new BadRequest({global:'Credentials not provided'});
    if(!userOpts.email || validator.isEmpty(userOpts.email) ) errors.email = 'Email not provided'
    if( userOpts.email && !validator.isEmail(userOpts.email) ) errors.email = 'Invalid Email';
    if(!userOpts.password || validator.isEmpty(userOpts.password) ) errors.password = 'Password not provided'

    if(!!Object.keys(errors).length)  throw new BadRequest(errors)
    else return true;
}

module.exports = {
    signup:signup,
    login:login
}