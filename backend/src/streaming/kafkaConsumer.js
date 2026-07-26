const { Kafka } = require('kafkajs');

const kafka = new Kafka({
  clientId: 'cirop-backend',
  brokers: ['localhost:19092'],
});

const consumer = kafka.consumer({ groupId: 'cirop-group' });
let io = null;

const startConsumer = async (socketIO) => {
  io = socketIO;
  await consumer.connect();
  
  // Subscribe to multiple topics
  await consumer.subscribe({ topic: 'customer_events', fromBeginning: true });
  await consumer.subscribe({ topic: 'orders', fromBeginning: true });
  await consumer.subscribe({ topic: 'alerts', fromBeginning: true });

  await consumer.run({
    eachMessage: async ({ topic, message }) => {
      const event = JSON.parse(message.value.toString());
      console.log(`[${topic}] Received:`, event.event_type || event.alert_type || 'order');
      
      if (io) {
        io.emit(topic, event);
      }
    },
  });
};

module.exports = { startConsumer };