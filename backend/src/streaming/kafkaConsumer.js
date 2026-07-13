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
  await consumer.subscribe({ topic: 'customer_events', fromBeginning: true });

  await consumer.run({
    eachMessage: async ({ message }) => {
      const event = JSON.parse(message.value.toString());
      console.log(`Received: ${event.event_type} | Customer ${event.customer_id}`);
      
      if (io) {
        io.emit('customer_event', event);
      }
    },
  });
};

module.exports = { startConsumer };