class Authorisation{
    constructor(props){
        this.status = 401;
        this.name = 'Authorisation Error'
        this.info = props
    }
}

class BadRequest{
    constructor(props){
        this.status = 400;
        this.name = 'Bad Request'
        this.info = props
}
}

class OutOfQuotas{
    constructor(props){
        this.status = 402;
        this.name = 'Out of quotas'
        this.info = props
    }
}

module.exports = {
    BadRequest : BadRequest,
    AuthError: Authorisation,
    OutOfQuotas: OutOfQuotas
}