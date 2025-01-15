const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
    startProcess: () => ipcRenderer.send('startProcess'),
    stopProcess: () => ipcRenderer.send('stopProcess'),
    isRunning: () => ipcRenderer.invoke('isRunning'),
    zookeeper: {
        onData: (callback) => ipcRenderer.on('zookeeper:data', callback),
        onError: (callback) => ipcRenderer.on('zookeeper:error', callback),
        onExit: (callback) => ipcRenderer.on('zookeeper:exit', callback),
    },
    kafka: {
        onData: (callback) => ipcRenderer.on('kafka:data', callback),
        onError: (callback) => ipcRenderer.on('kafka:error', callback),
        onExit: (callback) => ipcRenderer.on('kafka:exit', callback),
    },
});
