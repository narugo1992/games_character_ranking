from functools import lru_cache
from typing import Tuple, List

import numpy as np
import torch.cuda
from PIL import Image
from anime_face_detector import create_detector


@lru_cache()
def _get_detector(model='yolov3'):
    return create_detector(model, device='cuda' if torch.cuda.is_available() else 'cpu')


def fill_background(image: Image.Image, background: str = 'white') -> Image.Image:
    if image.mode == 'RGB':
        return image
    if image.mode != 'RGBA':
        image = image.convert('RGBA')

    background = background or 'white'
    result = Image.new('RGBA', image.size, background)
    result.paste(image, (0, 0), image)

    return result.convert('RGB')


def image_padding(image: Image.Image, width_padding: Tuple[int, int] = (0, 0),
                  height_padding: Tuple[int, int] = (0, 0), mode='edge'):
    if image.mode != 'RGB':
        image = image.convert('RGB')

    data = np.asarray(image)
    data = np.pad(data, (height_padding, width_padding, (0, 0)), mode=mode)
    return Image.fromarray(data, 'RGB')


def find_heads(image: Image.Image, threshold: float = 0.5,
               scale: Tuple[Tuple[float, float], Tuple[float, float]] = ((2.0, 2.5), (2.0, 1.5)),
               model='yolov3') -> List[Tuple[Image.Image, float]]:
    image = fill_background(image, background='white')
    scale = np.asarray(scale)
    data_pil = np.asarray(image)
    data_cv2 = data_pil[:, :, ::-1]

    detector = _get_detector(model)
    retval = []
    for pred in detector(data_cv2):
        bbox_raw = pred['bbox']
        box, score = bbox_raw[:4], float(bbox_raw[4])
        if score < threshold:
            continue

        box = box.reshape((2, 2))
        size = box[1] - box[0]
        align_offset = size.max() - size
        box[0] -= align_offset / 2
        box[1] += align_offset / 2
        center = box.mean(axis=0)
        box = (box - center) * scale + center

        padding_offset = (np.stack([
            -np.stack([np.asarray([0.0, 0.0]), box[0]]).min(axis=0),
            np.stack([np.asarray(image.size), box[1]]).max(axis=0) - np.asarray(image.size)
        ]) * 2).astype(np.int)
        current_image = image_padding(
            image,
            width_padding=tuple(padding_offset[:, 0]),
            height_padding=tuple(padding_offset[:, 1]),
        )

        retval.append((current_image.crop((box + padding_offset[0]).astype(np.int).reshape(4)), score))

    retval = sorted(retval, key=lambda x: -x[1])
    return retval
