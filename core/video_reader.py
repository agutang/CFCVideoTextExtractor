from services.i18n import tr
import math
import av

class VideoReader:
    def __init__(self, path):
        try:
            self.container = av.open(str(path))
            self.stream = self.container.streams.video[0]
        except Exception as exc:
            if hasattr(self, 'container'):
                self.container.close()
            raise ValueError(tr('영상을 열 수 없습니다: {0}').format(exc)) from exc
        self.width = self.stream.codec_context.width
        self.height = self.stream.codec_context.height
        self.fps = float(self.stream.average_rate) if self.stream.average_rate else 0
        self.origin = float(self.stream.start_time * self.stream.time_base) if self.stream.start_time is not None else None
        self.duration = float(self.stream.duration * self.stream.time_base) if self.stream.duration else float(self.container.duration or 0) / av.time_base

    def frames(self):
        previous = -1.0
        for frame in self.container.decode(self.stream):
            if frame.pts is None or frame.time_base is None:
                raise ValueError(tr('영상 프레임의 PTS가 없습니다. 정확한 시간 분석이 불가능합니다.'))
            raw = float(frame.pts * frame.time_base)
            if self.origin is None:
                self.origin = raw
            timestamp = raw - self.origin
            if not math.isfinite(timestamp) or timestamp < -1e-6 or timestamp < previous - 1e-6:
                raise ValueError(tr('영상 타임스탬프가 잘못되었거나 역행합니다.'))
            previous = max(0, timestamp)
            yield previous, frame.to_ndarray(format='bgr24')

    def at(self, seconds):
        # Seek to a keyframe, then decode forward to the first actual PTS >= target.
        if self.origin is None:
            next(self.frames())
        self.container.seek(int((seconds + self.origin) / float(self.stream.time_base)), stream=self.stream, backward=True)
        last = None
        for timestamp, image in self.frames():
            last = timestamp, image
            if timestamp + 1e-9 >= seconds:
                return last
        if last is None:
            raise ValueError(tr('해당 시점의 프레임을 읽을 수 없습니다.'))
        return last

    def close(self):
        self.container.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
