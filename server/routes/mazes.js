const router = require('express').Router();
const mazeController = require('../controllers/mazes/maze')
const { solve } = require('../controllers/mazes/solver/solver')

router.post('/', async (req,res) => {
    const token = req.headers['authorisation']
    try {
        const addMaze = await mazeController.addMaze(req.body.maze, token);
        res.send(addMaze);
    }catch(e){
        res.status(e.status).send(e.info);
    }
})

router.get('/', async (req,res) => {

    try {
        const mazes = await mazeController.info(false);
        res.send(mazes);
    }catch(e){
        res.status(e.status).send(e.info);
    }
})

router.get('/:mazeId', async (req,res) => {
    try {
        const maze = await mazeController.info(req.params.mazeId);
        res.send(maze);
    }catch(e){
        res.status(e.status).send(e.info);
    }
})

router.get('/:mazeId/solve', async (req,res) => {
    try {
        const maze = await mazeController.info(req.params.mazeId)
		const solution = solve(maze[0].maze)
        res.send(solution);
    }catch(e){
        res.status(e.status).send(e.info);
    }
})



module.exports = router;
