// Find free (not obstacle) adjacent nodes for 1d representation of 2d grid
const adjacent = ( currentIdx, maze, mazeSize = 14 ) => {
	let currentX = currentIdx % mazeSize
	let currentY = Math.floor(currentIdx / mazeSize)
	let res = []

	// Node to the right
	if (currentX < mazeSize - 1 && maze[currentIdx + 1] != 'X') res.push(currentIdx + 1)
	// Node to the left
	if (currentX > 0 && maze[currentIdx - 1] != 'X') res.push(currentIdx - 1)
	// Node to the top
	if (currentY < mazeSize - 1 && maze[currentIdx + mazeSize] != 'X') res.push(currentIdx + mazeSize)
	// Node to the bottom
	if (currentY > 0 && maze[currentIdx - mazeSize] != 'X') res.push(currentIdx - mazeSize)

	return res
}

module.exports = {
	adjacent: adjacent
}
