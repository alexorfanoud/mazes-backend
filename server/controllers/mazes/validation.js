const validator = require('validator')
const { BadRequest } = require('../../errors/models')

const validate = (maze, size) => {
    let startCounter = 0,targetCounter = 0;
    for(let i=0;i<maze.length;i++){
        maze[i]==='S' ? startCounter++ :
        maze[i]==='T' ? targetCounter++ : ''
        if(startCounter > 1 || targetCounter >1 ) {throw new BadRequest('Only one start and one target node allowed')} 
        if(maze[i]!=='X' && maze[i]!=='.' && maze[i]!=='S' && maze[i]!=='T' ) {
            throw new BadRequest({maze:`Invalid maze format, found a '${maze[i]}' at position ${i}`});
        }
    }
    if( maze.length % size != 0) {
        throw new BadRequest({maze:`Invalid declared sizeX for maze, expected sizeX of ${size} but got maze string of length ${maze.length}`})
    }
}

module.exports = {
    validate:validate
}
