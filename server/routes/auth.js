const router = require('express').Router()
const validationController = require('../controllers/users/validation')
const authController = require('../controllers/users/auth')

router.post( '/signup',async (req, res)=>{
    try{
        validationController.signup(req.body);
        const user = await authController.signup(req.body);
        res.send(user);
    }catch(e){
        res.status(e.status || 500).send(e.info)
    }        
})

router.post( '/login',async (req, res)=>{
    try{
        validationController.login(req.body);
        const userInfo = await authController.login(req.body);
        res.send(userInfo);
    }catch(e){
        res.status(e.status || 500).send(e.info)
    }        
})

router.post( 
    '/logout',
    require('../middlewares/user/auth').userRoute,
    async (req, res)=>{
        try{
            const result = await  authController.logout(req.headers['authorisation']);
            res.send(result);
        }catch(e){
            res.status(e.status || 500).send(e.info)
        }        
})

module.exports = router
