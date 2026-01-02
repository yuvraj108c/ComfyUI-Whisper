# ComfyUI Whisper

Transcribe audio and add subtitles to videos using [Whisper](https://github.com/openai/whisper/) in [ComfyUI](https://github.com/comfyanonymous/ComfyUI).
Support multiple languages, prompt guidance and multiple whisper models.

**Last tested**: 2 January 2026 (ComfyUI v0.7.0@f2fda02 | Torch 2.9.1 | Triton 3.5.1 | Python 3.10.12 | RTX4090 | CUDA 13.0 | Debian 12)

![demo-image](https://github.com/yuvraj108c/ComfyUI-Whisper/blob/assets/recording.gif?raw=true)

## ⭐ Support
If you like my projects and wish to see updates and new features, please consider supporting me. It helps a lot! 

[![ComfyUI-Depth-Anything-Tensorrt](https://img.shields.io/badge/ComfyUI--Depth--Anything--Tensorrt-blue?style=flat-square)](https://github.com/yuvraj108c/ComfyUI-Depth-Anything-Tensorrt)
[![ComfyUI-Upscaler-Tensorrt](https://img.shields.io/badge/ComfyUI--Upscaler--Tensorrt-blue?style=flat-square)](https://github.com/yuvraj108c/ComfyUI-Upscaler-Tensorrt)
[![ComfyUI-Dwpose-Tensorrt](https://img.shields.io/badge/ComfyUI--Dwpose--Tensorrt-blue?style=flat-square)](https://github.com/yuvraj108c/ComfyUI-Dwpose-Tensorrt)
[![ComfyUI-Rife-Tensorrt](https://img.shields.io/badge/ComfyUI--Rife--Tensorrt-blue?style=flat-square)](https://github.com/yuvraj108c/ComfyUI-Rife-Tensorrt)

[![ComfyUI-Whisper](https://img.shields.io/badge/ComfyUI--Whisper-gray?style=flat-square)](https://github.com/yuvraj108c/ComfyUI-Whisper)
[![ComfyUI_InvSR](https://img.shields.io/badge/ComfyUI__InvSR-gray?style=flat-square)](https://github.com/yuvraj108c/ComfyUI_InvSR)
[![ComfyUI-Thera](https://img.shields.io/badge/ComfyUI--Thera-gray?style=flat-square)](https://github.com/yuvraj108c/ComfyUI-Thera)
[![ComfyUI-Video-Depth-Anything](https://img.shields.io/badge/ComfyUI--Video--Depth--Anything-gray?style=flat-square)](https://github.com/yuvraj108c/ComfyUI-Video-Depth-Anything)
[![ComfyUI-PiperTTS](https://img.shields.io/badge/ComfyUI--PiperTTS-gray?style=flat-square)](https://github.com/yuvraj108c/ComfyUI-PiperTTS)

[![buy-me-coffees](https://i.imgur.com/3MDbAtw.png)](https://www.buymeacoffee.com/yuvraj108cZ)
[![paypal-donation](https://i.imgur.com/w5jjubk.png)](https://paypal.me/yuvraj108c)
---

## Installation

Install via [ComfyUI Manager](https://github.com/ltdrdata/ComfyUI-Manager)

## Usage

Load this [workflow](https://github.com/yuvraj108c/ComfyUI-Whisper/blob/master/example_workflows/whisper_video_subtitles_workflow.json) into ComfyUI

Models are auto-downloaded to `/ComfyUI/models/stt/whisper`

## Supported Models
'tiny.en', 'tiny', 'base.en', 'base', 'small.en', 'small', 'medium.en', 'medium', 'large-v1', 'large-v2', 'large-v3', 'large', 'large-v3-turbo', 'turbo'

## Nodes

### Apply Whisper

Transcribe audio and get timestamps for each segment and word.

### Add Subtitles To Frames

Add subtitles on the video frames. You can specify font family, font color and x/y positions.

### Add Subtitles To Background (Experimental)

Add subtitles like wordcloud on blank frames

### Save SRT

Export alignments as SRT files in `/ComfyUI/output/srt` directory

## Updates
### 2 January 2026
- Export alignments as SRT  
- Add `torchcodec` to requirements
### 27 August 2025
- Merge https://github.com/yuvraj108c/ComfyUI-Whisper/pull/22 by [@francislabountyjr](https://github.com/francislabountyjr) for model patcher, more whisper models support, comfyui model directory support
- Merge https://github.com/yuvraj108c/ComfyUI-Whisper/pull/18 by [@qy8502](https://github.com/qy8502) for Prompt Guidance support
- Support YRDZST Semibold Font
### 2 May 2025
- Merge https://github.com/yuvraj108c/ComfyUI-Whisper/pull/15 by [@niknah](https://github.com/niknah) for language selection

## Credits

- [comfyanonymous/ComfyUI](https://github.com/comfyanonymous/ComfyUI)

- [Kosinkadink/ComfyUI-VideoHelperSuite](https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite)

- [melMass/comfy_mtb](https://github.com/melMass/comfy_mtb)

## License

[Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)](https://creativecommons.org/licenses/by-nc-sa/4.0/)

