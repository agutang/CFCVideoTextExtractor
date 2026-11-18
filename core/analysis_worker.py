import copy
import logging
import threading
import time as clock
from PySide6.QtCore import QThread, Signal
from core.video_reader import VideoReader
from core.extraction_processor import Processor
from core.event_detector import EventDetector
from core.extraction_scheduler import Scheduler
from services.output_writer import OutputWriter

def analyze(frames, preset, processor, writer, log, progress, checkpoint=lambda: True):
    detector = EventDetector(preset.absence)
    scheduler = Scheduler(preset.delay)
    next_sample = 0.0
    completed = 0
    validated = False
    last_progress = 0.0
    for time, frame in frames:
        if not checkpoint():
            log('사용자가 분석을 중단했습니다. 기존 결과는 보존됩니다.')
            return
        if not validated:
            processor.validate(frame)
            validated = True
        if time + 1e-9 >= next_sample:
            previous = detector.present
            if detector.update(processor.detected(frame), time):
                event = scheduler.add(time)
                log(f'이벤트 #{event.id}: {time:.3f}초 → {event.target:.3f}초 예약')
            if previous != detector.present:
                log(f'{time:.3f}초 감지 상태: {detector.present}')
            next_sample = time + preset.interval
        for event in scheduler.due(time):
            if not checkpoint():
                log('사용자가 분석을 중단했습니다. 기존 결과는 보존됩니다.')
                return
            row = writer.write(processor.extract(frame), time)
            event.status = 'completed'
            completed += 1
            log(f'기록 #{event.id}: {row}')
        now = clock.monotonic()
        if now - last_progress >= .1:
            progress(time, scheduler.count, completed, len(scheduler.pending))
            last_progress = now
    if not validated:
        raise ValueError('영상에 디코딩 가능한 프레임이 없습니다.')
    for event in scheduler.pending:
        event.status = 'beyond_end'
        log(f'이벤트 #{event.id}: 영상 종료 이후 예약({event.target:.3f}초), 기록 제외')
    scheduler.pending.clear()
    progress(time, scheduler.count, completed, 0)

class AnalysisWorker(QThread):
    message = Signal(str)
    progress = Signal(float, int, int, int)
    failed = Signal(str)

    def __init__(self, path, preset, output, overwrite):
        super().__init__()
        self.path, self.preset = path, copy.deepcopy(preset)
        self.output, self.overwrite = output, overwrite
        self.condition = threading.Condition()
        self.paused = False
        self.stopped = False

    def pause(self, value):
        with self.condition:
            self.paused = value
            self.condition.notify_all()

    def stop(self):
        with self.condition:
            self.stopped = True
            self.condition.notify_all()

    def checkpoint(self):
        with self.condition:
            while self.paused and not self.stopped:
                self.condition.wait()
            return not self.stopped

    def log(self, text):
        logging.info(text)
        self.message.emit(text)

    def run(self):
        writer = None
        processor = None
        try:
            with VideoReader(self.path) as reader:
                processor = Processor(self.preset, self.log)
                frames = reader.frames()
                first = next(frames, None)
                if first is None:
                    raise ValueError('빈 영상입니다.')
                processor.validate(first[1])
                writer = OutputWriter(self.output, self.overwrite)
                from itertools import chain
                analyze(chain([first], frames), self.preset, processor, writer, self.log,
                        self.progress.emit, self.checkpoint)
                self.log('분석 작업이 종료되었습니다.')
        except Exception as exc:
            logging.exception('분석 실패')
            self.failed.emit(f'분석 실패: {exc}')
        finally:
            if writer:
                writer.close()
            if processor:
                processor.close()
