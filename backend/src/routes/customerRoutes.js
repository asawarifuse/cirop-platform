const express = require('express');
const router = express.Router();
const customerController = require('../controllers/customerController');
const { authenticate } = require('../middleware/auth');

router.use(authenticate);

router.get('/', customerController.getAllCustomers);
router.get('/:id', customerController.getCustomerById);

module.exports = router;