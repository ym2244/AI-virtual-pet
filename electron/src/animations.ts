import fs from "fs";
import path from "path";

// **BASE_DIR 设定动画根目录**
const BASE_DIR = path.join(__dirname, "..", "images");

// **动态读取文件夹内所有 PNG 文件**
function getFrames(folder: string): string[] {
    const dirPath = path.join(BASE_DIR, folder);
    try {
        return fs.readdirSync(dirPath)
            .filter(file => file.endsWith(".png"))
            .map(file => `../images/${folder}/${file}`);
    } catch (error) {
        console.error(`❌ 读取动画帧失败: ${dirPath}`, error);
        return [];
    }
}

// **动画类型**
const animations = {
    default: getFrames("Default/Happy/1"),
    speaking: getFrames("Say/Shining/B_2"),
    startup: getFrames("StartUP/Nomal"),
    raised: getFrames("Raise/Raised_Dynamic/Happy")
};

export { animations };
