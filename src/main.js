const path = require('path');
const { app, BrowserWindow, ipcMain } = require('electron');
const Store = require('electron-store');
const axios = require('axios');
const kafka = require('./lib/kafka');

const { spawn, execSync } = require('child_process');

let mainWindow = null;
const zookeeperLogs = [];
const kafkaLogs = [];

console.log(app.getPath('userData'));

const createWindow = () => {
    // Create the browser window.
    mainWindow = new BrowserWindow({
        width: 800,
        height: 600,
        webPreferences: {
            preload: path.join(__dirname, 'lib/preload.js'),
        },
    });

    // and load the index.html of the app.
    mainWindow.loadFile(path.join(__dirname, 'views/index.html'));

    // Open the DevTools.
    // mainWindow.webContents.openDevTools();

    mainWindow.on('closed', () => {
        mainWindow = null;
    });
};

const handleStartProcess = () => {
    const process = spawn('./src/assets/app2');
    // const process = spawn('python3', ['./src/assets/app.py']);

    // console.log(text.toString());

    console.log('here1');
    // const text2 = execSync('python3 ./src/assets/app2.py');

    // console.log(text2.toString());

    // console.log('here2');
    process.stdout.on('data', (data) => {
        console.log(data.toString());
    });

    process.stderr.on('data', (data) => {
        console.error(data.toString());
    });

    process.on('error', (err) => {
        console.log('Error');
        console.log(err);
    });
    // kafka.startZookeeperProcess({
    //     onData: (content) => {
    //         mainWindow.webContents.send('zookeeper:data', content);
    //         zookeeperLogs.push(content);
    //     },
    //     onError: (content) => {
    //         mainWindow.webContents.send('zookeeper:error', content);
    //         zookeeperLogs.push(content);
    //     },
    //     onExit: (message) => {
    //         mainWindow.webContents.send('zookeeper:exit', message);
    //         zookeeperLogs.push(message);
    //     },
    // });
    // kafka.startKafkaProcess({
    //     onData: (content) => {
    //         mainWindow.webContents.send('kafka:data', content);
    //         kafkaLogs.push(content);
    //     },
    //     onError: (content) => {
    //         mainWindow.webContents.send('kafka:error', content);
    //         zookeeperLogs.push(content);
    //     },
    //     onExit: (message) => {
    //         mainWindow.webContents.send('kafka:exit', message);
    //         zookeeperLogs.push(message);
    //     },
    // });
};

const stopProcess = async () => {
    // kafka.stopZookeeperProcess();
    // kafka.stopKafkaProcess();

    try {
        const { data } = await axios.get('http://localhost:5004/transcribe');
        console.log(data);
    } catch (err) {
        console.log(err);
    }
};

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.whenReady().then(() => {
    createWindow();

    ipcMain.on('startProcess', handleStartProcess);
    ipcMain.on('stopProcess', stopProcess);
    ipcMain.handle('isRunning', kafka.isRunning);

    app.on('activate', () => {
        // On macOS it's common to re-create a window in the app when the
        // dock icon is clicked and there are no other windows open.
        if (BrowserWindow.getAllWindows().length === 0) createWindow();
    });
});

// Quit when all windows are closed, except on macOS. There, it's common
// for applications and their menu bar to stay active until the user quits
// explicitly with Cmd + Q.
app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') app.quit();
});
