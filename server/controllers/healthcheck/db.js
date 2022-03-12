const { query, getConnection } = require('../../DB')

const check = async () => {

	const healthcheck = await query('SELECT 1 FROM user WHERE Id=0');
	return {"status": "ok"}
}


module.exports = {
    check:check
}
