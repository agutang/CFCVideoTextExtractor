import cv2
import numpy as np

class ImageDetector:
    def __init__(self):
        self.cache = {}

    def load(self, path):
        if path not in self.cache:
            try:
                image = cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
            except (OSError, ValueError) as exc:
                raise ValueError(f'기준 이미지를 읽을 수 없습니다: {path}') from exc
            if image is None:
                raise ValueError(f'이미지가 손상되었습니다: {path}')
            self.cache[path] = image
        return self.cache[path]

    def score(self, frame, region, path, scales):
        roi = cv2.cvtColor(region.crop(frame), cv2.COLOR_BGR2GRAY)
        template = self.load(path)
        best = -1.0
        fits = False
        for scale in scales:
            width, height = max(1, round(template.shape[1]*scale)), max(1, round(template.shape[0]*scale))
            if width > roi.shape[1] or height > roi.shape[0]:
                continue
            fits = True
            resized = cv2.resize(template, (width, height))
            # Normalized correlation is undefined for constant templates.
            if resized.std() < 1e-6:
                error = float(cv2.minMaxLoc(cv2.matchTemplate(roi, resized, cv2.TM_SQDIFF))[0])
                value = 1 - error / (width * height * 255.0**2)
            else:
                value = float(cv2.minMaxLoc(cv2.matchTemplate(roi, resized, cv2.TM_CCOEFF_NORMED))[1])
            best = max(best, value)
        if not fits:
            raise ValueError('모든 스케일의 기준 이미지가 탐색 영역보다 큽니다.')
        return best
