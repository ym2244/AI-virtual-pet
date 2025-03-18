"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.animations = void 0;
const fs_1 = __importDefault(require("fs"));
const path_1 = __importDefault(require("path"));
// **BASE_DIR 设定动画根目录**
const BASE_DIR = path_1.default.join(__dirname, "..", "images");
// **动态读取文件夹内所有 PNG 文件**
function getFrames(folder) {
    const dirPath = path_1.default.join(BASE_DIR, folder);
    try {
        return fs_1.default.readdirSync(dirPath)
            .filter(file => file.endsWith(".png"))
            .map(file => `../images/${folder}/${file}`);
    }
    catch (error) {
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
exports.animations = animations;
