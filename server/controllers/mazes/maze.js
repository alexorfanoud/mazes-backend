const { query, getConnection } = require('../../DB')
const { BadRequest } = require('../../errors/models')
const { validate } = require('./validation')
const jwt = require('jsonwebtoken')

const info = async (id) => {

        if(!id) {
            const mazes = await query('SELECT Id,maze FROM mazes');

            return mazes.map( maze => ({Id:(maze.Id.toString()), maze:Array.from(maze.maze)}))
        }
        else {
            const maze = await query('SELECT maze FROM mazes WHERE Id=?', [id]);
            if(maze.length === 0) throw new BadRequest({maze:'Maze doesnt exist'});
            return [{maze:Array.from(maze[0].maze)}]
        }
}
const creator_info = async (creator_name) => {

    if(!creator_name) {
        const mazes = await query('SELECT Id,maze FROM mazes');

        return mazes.map( maze => ({Id:(maze.Id.toString()), maze:Array.from(maze.maze)}))
    }
    else {
        const creator_id = await query('SELECT Id FROM user WHERE email=?',[creator_name])
        const mazes = await query('SELECT maze FROM mazes WHERE creator=?', [creator_id]);
        return mazes.map( maze => ({Id:(maze.Id.toString()), maze:Array.from(maze.maze)}))
    }
}
const addMaze = async ( maze, token ) => {
    try{
        const decoded = await jwt.decode(token);
        const userId = decoded._id;
        validate(maze);
        const creator = await query('SELECT email FROM user WHERE Id=?', [userId]);
        const result = await query('INSERT INTO mazes(maze,creator) VALUES (?,?)', [maze, userId]);
        
        return [{ Id:result.insertId.toString(), maze:Array.from(maze) }]
    }
    catch(e){
        throw new BadRequest({msg:e.message})
    }
        

}

module.exports = {
    info:info,
    addMaze:addMaze,
    creator_info:creator_info
}