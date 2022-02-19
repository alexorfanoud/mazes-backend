const { query, getConnection } = require('../../DB')
const { BadRequest } = require('../../errors/models')
const { validate } = require('./validation')
const { manhattanHeur } = require('./heuristics')
const { adjacent } = require('./utils')
const { HashMap } = require('../../dataStructures/HashMap')
const { PriorityQueue } = require('../../dataStructures/PriorityQueue')
const jwt = require('jsonwebtoken')

const info = async (id) => {

        if(!id) {
            const mazes = await query('SELECT Id,maze,sizeX FROM mazes');

            return mazes.map( maze => ({Id:(maze.Id.toString()), maze:Array.from(maze.maze), sizeX:maze.sizeX}))
        }
        else {
            const maze = await query('SELECT maze, sizeX FROM mazes WHERE Id=?', [id]);
            if(maze.length === 0) throw new BadRequest({maze:'Maze doesnt exist'});
            return [{maze:Array.from(maze[0].maze), sizeX:maze[0].sizeX}]
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

const add = async ( maze, size, token ) => {
    try{
        const decoded = await jwt.decode(token);
        const userId = decoded._id;
        validate(maze, size);
        const result = await query('INSERT INTO mazes(maze,sizeX,creator) VALUES (?,?,?)', [maze, size, userId]);
        
        return [{ Id:result.insertId.toString(), maze:Array.from(maze) }]
    }
    catch(e){
		if (e instanceof BadRequest) { throw e }
		else throw new BadRequest({msg:e.message})
    }
}
        
const solve = ( maze, sizeX ) => {

	// Find start and finish
	let start = maze.indexOf("S")
	let target = maze.indexOf("T")

    let visited = [], path = [], current;
    let distances = new HashMap(); distances.set(start,0);
    let previous = new HashMap(); previous.set(start,-1);

	// Function to evaluate the distance of a specific node from the target
    let nodeEvaluation = ( nodeIdx ) => manhattanHeur( nodeIdx, target, sizeX )
	// Priority queue to decide which node to visit first on every iteration
    let toVisit = new PriorityQueue();
    toVisit.push(start,nodeEvaluation(start))

    while( toVisit.length() > 0 ){
        current  = toVisit.shift();
        if( current === target ){
			// If we have reached target, go to the previous of each node to find the complete path calculated
            while( current !== start ){
                path.unshift(current);
                current = previous.get(current);
            };
			// Remove the target from being 2 times in the visited nodes and the path
            visited.shift(); path.pop();
            return { visited: visited, path:path}
        }
        visited.push(current);

		// For each adjacent node, calculate their estimated distance from target if we haven't already
        adjacent(current,maze,sizeX).map( adj => {
            if(!previous.has(adj)){
                previous.set(adj,current)
                distances.set(adj,distances.get(current)+1)
                toVisit.push(adj,nodeEvaluation(adj))
            }
            return adj
        })
    }

    visited.shift();
    return { visited: visited, path:path}
}

const generate = async ( size ) => {
    try{
		maze = ".....................ST............."
        
        return { maze:Array.from(maze) }
    }
    catch(e){
		if (e instanceof BadRequest) { throw e }
		else throw new BadRequest({msg:e.message})
    }
}

module.exports = {
    info:info,
    add:add,
    creator_info:creator_info,
	generate: generate,
	solve: solve
}
