const fs = require('fs');
const fsAsync = require('fs/promises');
const { spawn } = require('child_process');
const Store = require('electron-store');

// Store.set('zookeeper')

const defaultCallbackObj = {
    onData: () => {},
    onError: () => {},
    onExit: () => {},
};

let zookeeperService = null;
let kafkaService = null;

const removeKafkaTempDirs = async () => {
    if (fs.existsSync('/tmp/zookeeper')) {
        await fsAsync.rm('/tmp/zookeeper', { recursive: true });
    }

    if (fs.existsSync('/tmp/kafka-logs')) {
        await fsAsync.rm('/tmp/kafka-logs', { recursive: true });
    }
};

const startZookeeperProcess = async (callbackObj = defaultCallbackObj) => {
    if (!zookeeperService) {
        await removeKafkaTempDirs();

        console.log('Starting zookeeper...');

        zookeeperService = spawn('/Users/developer007/Development/kafka_2.13-3.2.0/bin/zookeeper-server-start.sh', [
            '/Users/developer007/Development/kafka_2.13-3.2.0/config/zookeeper.properties',
        ]);

        zookeeperService.stdout.on('data', async (chunk) => {
            callbackObj.onData(chunk.toString());
        });

        zookeeperService.stderr.on('data', async (chunk) => {
            callbackObj.onError(chunk.toString());
        });

        zookeeperService.on('exit', async (code) => {
            zookeeperService = null;

            callbackObj.onExit('Zookeeper process exited with code: ' + code);
        });
    }
};

const stopZookeeperProcess = () => {
    console.log('Stopping zookeeper...');

    spawn('/Users/developer007/Development/kafka_2.13-3.2.0/bin/zookeeper-server-stop.sh');
};

const startKafkaProcess = (callbackObj = defaultCallbackObj) => {
    if (!kafkaService) {
        console.log('Starting kafka...');

        kafkaService = spawn('/Users/developer007/Development/kafka_2.13-3.2.0/bin/kafka-server-start.sh', [
            '/Users/developer007/Development/kafka_2.13-3.2.0/config/server.properties',
        ]);

        kafkaService.stdout.on('data', async (chunk) => {
            callbackObj.onData(chunk.toString());
        });

        kafkaService.stderr.on('data', async (chunk) => {
            callbackObj.onError(chunk.toString());
        });

        kafkaService.on('exit', async (code) => {
            kafkaService = null;

            callbackObj.onExit('Kafka process exited with code: ' + code);
        });
    }
};

const stopKafkaProcess = () => {
    console.log('Stopping kafka...');

    spawn('/Users/developer007/Development/kafka_2.13-3.2.0/bin/kafka-server-stop.sh');
};

module.exports = {
    startZookeeperProcess,
    stopZookeeperProcess,
    startKafkaProcess,
    stopKafkaProcess,
    isRunning: () => zookeeperService !== null || kafkaService !== null,
};
