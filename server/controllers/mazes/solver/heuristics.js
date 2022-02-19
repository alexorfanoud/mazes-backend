// Manhattan heuristic for 1d representation of 2d grid
const manhattanHeur = ( startIdx, targetIdx, mazeSize = 14 ) => {
	const distY = Math.floor(startIdx / mazeSize) - Math.floor(targetIdx / mazeSize)
	const distX = (startIdx % mazeSize) - (targetIdx % mazeSize)
	return Math.abs(distY) + Math.abs(distX)
}

module.exports = {
	manhattanHeur: manhattanHeur
}
