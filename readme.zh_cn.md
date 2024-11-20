# ComfyUI Whisper Translator
<div align="center">
<a href="./readme.md">English</a>
<a href="./readme.zh_cn.md">中文简体</a>
</div>
请多多star⭐

## 描述
这是一个 ComfyUI 节点，允许您使用 Whisper 翻译字幕。

现在支持多种语言：

[“zh”、“en”、“ja”、“ko”、“ru”、“fr”、“de”、“es”、“pt”、“it”、“ar”]

您可能需要将字体放在“fonts”文件夹中以支持不同的语言。

****
感谢以下项目的帮助：

ComfyUI 

[ComfyUI-Whisper](https://github.com/yuvraj108c/ComfyUI-Whisper)

[ComfyUI-WhisperX](https://github.com/AIFSH/ComfyUI-WhisperX)

## 效果截图
![en-image](https://github.com/civen-cn/ComfyUI-Whisper-Translator/blob/master/example/en.png?raw=true)
![zh-image](https://github.com/civen-cn/ComfyUI-Whisper-Translator/blob/master/example/zh.png?raw=true)
![ru-image](https://github.com/civen-cn/ComfyUI-Whisper-Translator/blob/master/example/ru.png?raw=true)
![es-image](https://github.com/civen-cn/ComfyUI-Whisper-Translator/blob/master/example/es.png?raw=true)
![ja-image](https://github.com/civen-cn/ComfyUI-Whisper-Translator/blob/master/example/jp.png?raw=true)

## 安装

通过[ComfyUI Manager](https://github.com/ltdrdata/ComfyUI-Manager)

## 用法
[workflow](https://github.com/civen-cn/ComfyUI-Whisper-Translator/blob/master/example_workflows/video_translation_subtitles_workflow.json)

## 节点

### Apply Whisper X

转录音频并获取每个片段（翻译）和单词的时间戳。

### Add Subtitles To Frames X

在视频帧上添加字幕。您可以指定字体系列、字体颜色（背景颜色）和 x/y 位置。

## 致谢
- [comfyanonymous/ComfyUI](https://github.com/comfyanonymous/ComfyUI)

- [Kosinkadink/ComfyUI-VideoHelperSuite](https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite)

- [melMass/comfy_mtb](https://github.com/melMass/comfy_mtb)

- [ComfyUI-Whisper](https://github.com/yuvraj108c/ComfyUI-Whisper)

- [ComfyUI-WhisperX](https://github.com/AIFSH/ComfyUI-WhisperX)



