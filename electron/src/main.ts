import { app, BrowserWindow } from "electron";

let mainWindow: BrowserWindow | null;

app.whenReady().then(() => {
  mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      nodeIntegration: true,
    },
  });

  mainWindow.loadFile("index.html");
  
  mainWindow.on("closed", () => {
    mainWindow = null;
  });
});
