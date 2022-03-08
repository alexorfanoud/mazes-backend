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

const highscoreAvg = async (mazeId) => {

    const highscoreAvg = await query(`
		SELECT avg(hs.score)
		from
			highscores hs
			inner join mazes m on m.Id = hs.mazeId
		where
			m.Id = ?
		`, [mazeId]);

	return highscoreAvg
}

const getBestScoreUser = async (mazeId) => {

    const bestUsers = await query(`
		SELECT 
			u.email,
			hs.score,
			hs.created_at
		FROM 
			highscores hs
			inner join user u on u.Id=hs.userId
		WHERE
			score = (select max(score) from highscores where mazeId = ?)
			and mazeId = ?
		`, [mazeId, mazeId]);

	return bestUsers
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
        
const addHighscore = async ( mazeId, token, score, created_at ) => {
    try{
        const decoded = await jwt.decode(token);
        const userId = decoded._id;
        const result = await query('INSERT INTO highscores(mazeId,userId,score,created_at) VALUES (?,?,?,?)', [mazeId, userId, score, created_at]);
        
        return result
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

const generate = async ( size, density = 1.2, difficulty = 100 ) => {
    try{
		// Fill array based on the provided obstacle density
		maze = Array(size*size)
			.fill()
			.map((_, elem) => {return Math.floor(Math.random() * density) === 1 ? "X" : "."})

		// Generate random start point 
		startIdx = Math.floor(Math.random() * (size * size - 1))
		maze[startIdx] = "S"

		// Solve the maze to find all the points that can be reached
		const {visited, path} = solve(maze, size)
		
		// Set the target position as one of the reachable nodes on the grid
		const targetPos = visited[Math.floor((visited.length-1) * (difficulty/100))];
		maze[targetPos] = "T"

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
	generate: generate,
	solve: solve,
	highscoreAvg: highscoreAvg,
	getBestScoreUser: getBestScoreUser,
	addHighscore: addHighscore
}
