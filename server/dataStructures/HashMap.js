class HashMap { 
    constructor(){
       this.map = {};
    }
    set(key,value) {                                                                              
        this.map[JSON.stringify(key)] = value;
        return this.map        
    }
    has(key) { return this.map[JSON.stringify(key)] !== undefined }
    entries() {
        Object.keys(this.map).map( key => [key,this.map[key]])
	}
    get(key) { return this.map[JSON.stringify(key)] }
    delete(key) {return delete this.map[JSON.stringify(key)]}
} 

module.exports = {
	HashMap: HashMap
}
