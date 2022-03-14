const router = require('express').Router();
const mazeController = require('../controllers/mazes/maze')

router.post('/', async (req,res) => {
    const token = req.headers['authorisation']
    try {
        const addMaze = await mazeController.add(req.body.maze, parseInt(req.body.sizeX), token);
        res.send(addMaze);
    }catch(e){
        res.status(e.status || 500).send(e.info);
    }
})

router.get('/heavyQuery', async (req,res) => {

    try {
        const heavyQuery = await mazeController.heavyQuery();
        res.send(heavyQuery);
    }catch(e){
        res.status(e.status || 500).send(e.info);
    }
})

router.get('/generate', async (req,res) => {
    try {
        const maze = await mazeController.generate(parseInt(req.body.size))
        res.send(maze);
    }catch(e){
		console.log(e)
        res.status(e.status || 500).send(e.info);
    }
})

router.get('/:mazeId', async (req,res) => {
    try {
        const maze = await mazeController.info(req.params.mazeId);
        res.send(maze);
    }catch(e){
        res.status(e.status || 500).send(e.info);
    }
})

router.get('/:mazeId/solve', async (req,res) => {
    try {
        const maze = await mazeController.info(req.params.mazeId)
		const solution = mazeController.solve(maze[0].maze, maze[0].sizeX)
        res.send(solution);
    }catch(e){
        res.status(e.status || 500).send(e.info);
    }
})

router.get('/:mazeId/hsAvg', async (req,res) => {

    try {
        const highscoreAvg = await mazeController.highscoreAvg(req.params.mazeId);
        res.send(highscoreAvg);
    }catch(e){
        res.status(e.status || 500).send(e.info);
    }
})

router.get('/:mazeId/bestScoreUser', async (req,res) => {

    try {
        const bestUser = await mazeController.getBestScoreUser(req.params.mazeId);
        res.send(bestUser);
    }catch(e){
        res.status(e.status || 500).send(e.info);
    }
})

router.post('/:mazeId/highscores', async (req,res) => {

    const token = req.headers['authorisation']
    try {
        const newHighscore = await mazeController.addHighscore(req.params.mazeId, token, req.body.score, req.body.created_at);
        res.send(newHighscore);
    }catch(e){
        res.status(e.status || 500).send(e.info);
    }
})

router.get('/', async (req,res) => {

    try {
        const mazes = await mazeController.info(false);
        res.send(mazes);
    }catch(e){
        res.status(e.status || 500).send(e.info);
    }
})

module.exports = router;
