const validator = require('validator')
const { BadRequest } = require('../../errors/models')

const validate = (maze) => {
    let startCounter,targetCounter = 0;
    for(let i=0;i<maze.length;i++){
        maze[i]==='S' ? startCounter++ :
        maze[i]==='T' ? targetCounter++ : ''
        if(startCounter > 1 || targetCounter >1 ) {throw BadRequest('Only one start and one target node allowed')} 
        if(maze[i]!=='X' && maze[i]!=='.' && maze[i]!=='S' && maze[i]!=='T' ) {
            throw new BadRequest({maze:`Invalid maze format, found a ${maze[i]}`});
        }
    }
    if( maze.length !== 196 ) {
        throw new BadRequest({maze:`Invalid maze format, expected 196 blocks, got ${maze.length}`})
    }
}

module.exports = {
    validate:validate
}