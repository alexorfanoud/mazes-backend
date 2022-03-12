const router = require('express').Router();
const dbHealthcheckController = require('../controllers/healthcheck/db')

router.get('/db', async (req,res) => {
    try {
        const healthcheck = await dbHealthcheckController.check();
        res.send(healthcheck);
    }catch(e){
        res.status(e.status || 500).send(e.info);
    }
})


module.exports = router;
