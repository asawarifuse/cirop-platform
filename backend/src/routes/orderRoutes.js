const express = require('express');
const router = express.Router();
const orderController = require('../controllers/orderController');
const { authenticate } = require('../middleware/auth');

router.use(authenticate);

router.get('/analytics/revenue', orderController.getRevenueAnalytics);
router.get('/analytics/products', orderController.getProductPerformance);
router.get('/analytics/frequency', orderController.getPurchaseFrequency);
router.get('/analytics/aov', orderController.getAverageOrderValue);

module.exports = router;