const expect = require('chai').expect;
const validationController = require('../../../../controllers/users/validation')
const authController = require('../../../../controllers/users/auth')
const sinon = require('sinon')

describe('Signup Validation :', () => {

        it('Is a function',()=>{
            expect(validationController.signup).to.be.a('function')
        })

        describe('Validates user credentials', () => {
            it('Throws error if no credentials provided', () => {
                try{
                    validationController.signup({})
                }catch(e){

                    expect(e.status).to.equal(400);
                    expect(e.name).to.equal('Bad Request')
                    expect(e.info[e.name]).to.deep.equal({ global: 'Credentials not provided'})
                }
            })
    
            it('Throws error if no email/invalid email is provided', () => {
                try{
                    validationController.signup({password:'123',passConfirmation:'123'})
                }catch(e){
                    expect(e.status).to.equal(400);
                    expect(e.name).to.equal('Bad Request')
                    expect(e.info[e.name]).to.deep.equal({email:'Email not provided'})
                }
                try{
                    validationController.signup({password:'123',passConfirmation:'123',email:'123'})
                }catch(e){
                    expect(e.status).to.equal(400);
                    expect(e.name).to.equal('Bad Request')
                    expect(e.info[e.name]).to.deep.equal({email:'Invalid Email'})
                }
                try{
                    validationController.signup({password:'123',passConfirmation:'123',email:''})
                }catch(e){
                    expect(e.status).to.equal(400);
                    expect(e.name).to.equal('Bad Request')
                    expect(e.info[e.name]).to.deep.equal({email:'Email not provided'})
                }

            })
            
            it('Throws error if no password is provided', () => {
                try{
                    validationController.signup({email:'a@a.com',passConfirmation:'123'})
                }catch(e){
                    expect(e.status).to.equal(400);
                    expect(e.name).to.equal('Bad Request')
                    expect(e.info[e.name]).to.deep.equal({password:'Password not provided'})
                }
                try{
                    validationController.signup({email:'a@a.com',passConfirmation:'123',password:''})
                }catch(e){
                    expect(e.status).to.equal(400);
                    expect(e.name).to.equal('Bad Request')
                    expect(e.info[e.name]).to.deep.equal({password:'Password not provided'})
                }
            })
            it('Throws error if no password confirmation is provided', () => {
                try{
                    validationController.signup({email:'a@a.com',password:'123'})
                }catch(e){
                    expect(e.status).to.equal(400);
                    expect(e.name).to.equal('Bad Request')
                    expect(e.info[e.name]).to.deep.equal({passConfirmation:'Password confirmation not provided'})
                }
                try{
                    validationController.signup({email:'a@a.com',password:'123', passConfirmation:''})
                }catch(e){
                    expect(e.status).to.equal(400);
                    expect(e.name).to.equal('Bad Request')
                    expect(e.info[e.name]).to.deep.equal({passConfirmation:'Password confirmation not provided'})
                }
            })
            it('Throws error if password and password confirmation dont match', () => {
                try{
                    validationController.signup({email:'a@a.com',password:'123', passConfirmation:'132'})
                }catch(e){
                    expect(e.status).to.equal(400);
                    expect(e.name).to.equal('Bad Request')
                    expect(e.info[e.name]).to.deep.equal({passConfirmation:'Passwords dont match'})
                }
                
            })
            it('Doesnt throw on valid credentials', () => {
                try{
                    expect(validationController.signup({email:'a@a.com',password:'123', passConfirmation:'123'})).to.be.true
                    
                }catch(e){
                    expect.fail();
                }
                
            })


     

    

        })
    })

