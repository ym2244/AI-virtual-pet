"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const electron_1 = require("electron");
electron_1.contextBridge.exposeInMainWorld("electron", {
    getAnimationFrames: (animationPath) => electron_1.ipcRenderer.invoke("get-animation-frames", animationPath),
});
