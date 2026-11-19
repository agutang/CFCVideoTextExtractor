from dataclasses import dataclass, field, asdict, fields
from uuid import uuid4
import math

@dataclass
class Region:
    x: int = 0
    y: int = 0
    width: int = 100
    height: int = 100

    def validate(self, width, height):
        if any(type(v) is not int for v in asdict(self).values()):
            raise ValueError('영역 좌표는 정수여야 합니다.')
        if self.x < 0 or self.y < 0 or self.width <= 0 or self.height <= 0 or self.x + self.width > width or self.y + self.height > height:
            raise ValueError(f'영역이 영상 범위를 벗어납니다: {self}')

    def crop(self, frame):
        self.validate(frame.shape[1], frame.shape[0])
        return frame[self.y:self.y+self.height, self.x:self.x+self.width]

@dataclass
class ExtractionItem:
    name: str = '새 항목'
    kind: str = 'ocr'
    region: Region = field(default_factory=Region)
    enabled: bool = True
    id: str = field(default_factory=lambda: str(uuid4()))
    image: str = ''
    threshold: float = .9
    scales: list[float] = field(default_factory=lambda: [1.0])
    language: str = 'eng'
    fallback: str = ''
    zoom: float = 2.0
    grayscale: bool = True
    binary: bool = False
    denoise: bool = False
    contrast: float = 1.0
    present_text: str = 'True'
    absent_text: str = 'False'

@dataclass
class Preset:
    schema_version: int = 1
    name: str = '기본 설정'
    image: str = ''
    region: Region = field(default_factory=Region)
    threshold: float = .9
    scales: list[float] = field(default_factory=lambda: [1.0])
    interval: float = .2
    delay: float = 0.0
    absence: float = 0.0
    output_template: str = ''
    output_directory: str = ''
    items: list[ExtractionItem] = field(default_factory=list)

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        data = dict(data)
        if data.get('schema_version') != 1:
            raise ValueError('지원하지 않는 프리셋 버전입니다.')
        data['region'] = Region(**data['region'])
        data['items'] = [ExtractionItem(**{**{k: v for k, v in i.items() if k in {f.name for f in fields(ExtractionItem)}}, 'region': Region(**i['region'])}) for i in data['items']]
        result = cls(**data)
        result.validate()
        return result

    def validate(self):
        for value in (self.interval, self.delay, self.absence):
            if not math.isfinite(value) or value < 0:
                raise ValueError('시간은 0 이상의 유한한 값이어야 합니다.')
        for obj in [self, *self.items]:
            if not math.isfinite(obj.threshold) or not 0 <= obj.threshold <= 1:
                raise ValueError('유사도는 0~1이어야 합니다.')
            if not obj.scales or any(not math.isfinite(s) or s <= 0 or s > 10 for s in obj.scales):
                raise ValueError('스케일은 0 초과 10 이하입니다.')
        if len({i.id for i in self.items}) != len(self.items):
            raise ValueError('항목 ID가 중복되었습니다.')
        from services.text_format import validate_template
        validate_template(self.output_template, [i.name for i in self.items if i.enabled])
        for item in self.items:
            if item.kind not in ('ocr', 'image'):
                raise ValueError('알 수 없는 항목 유형입니다.')
            if not .1 <= item.zoom <= 10 or not .1 <= item.contrast <= 10:
                raise ValueError('OCR 확대/대비는 0.1~10이어야 합니다.')
