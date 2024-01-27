import torch
import numpy as np
from PIL import Image

# https://github.com/melMass/comfy_mtb/blob/501c3301056b2851555cccd75ab3ff15b1ab8e0c/utils.py#L261-L298
def tensor2pil(image):
    batch_count = image.size(0) if len(image.shape) > 3 else 1
    if batch_count > 1:
        out = []
        for i in range(batch_count):
            out.extend(tensor2pil(image[i]))
        return out

    return [
        Image.fromarray(
            np.clip(255.0 * image.cpu().numpy().squeeze(), 0, 255).astype(np.uint8)
        )
    ]

def pil2tensor(image):
    if isinstance(image, list):
        return torch.cat([pil2tensor(img) for img in image], dim=0)

    return torch.from_numpy(np.array(image).astype(np.float32) / 255.0).unsqueeze(0)

# https://github.com/comfyanonymous/ComfyUI/blob/fc196aac80fd~4bf6c8a39d85d1e809902871cade/comfy_extras/nodes_mask.py#L127
def tensor2Mask(image):
    return image[:, :, :, 0]