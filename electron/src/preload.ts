import { contextBridge, ipcRenderer } from "electron";

contextBridge.exposeInMainWorld("electron", {
    getAnimationFrames: (animationPath: string) => ipcRenderer.invoke("get-animation-frames", animationPath),
});
