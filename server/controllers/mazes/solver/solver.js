const { manhattanHeur } = require('./heuristics')
const { adjacent } = require('./utils')
const { HashMap } = require('../../../dataStructures/HashMap')
const { PriorityQueue } = require('../../../dataStructures/PriorityQueue')

const solve = ( maze ) => {

	// Find start and finish
	let start = maze.indexOf("S")
	let target = maze.indexOf("T")

    let visited = [], path = [], current;
    let distances = new HashMap(); distances.set(start,0);
    let previous = new HashMap(); previous.set(start,-1);

	// Function to evaluate the distance of a specific node from the target
    let nodeEvaluation = ( nodeIdx ) => manhattanHeur( nodeIdx, target )
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
        adjacent(current,maze).map( adj => {
            if(!previous.has(adj)){
                previous.set(adj,current);
                distances.set(adj,distances.get(current)+1)
                toVisit.push(adj,nodeEvaluation(adj))
            }
            return adj
        })
    }

    visited.shift();
    return { visited: visited, path:path}
}

module.exports = {
	solve: solve
}
