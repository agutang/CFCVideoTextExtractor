from services.i18n import tr
import copy
import json
from pathlib import Path, PurePosixPath
import uuid
import zipfile
from models.preset import Preset

def references(preset):
    yield preset
    yield from (i for i in preset.items if i.kind == 'image')

def save(preset, path):
    preset.validate()
    path = Path(path)
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(preset.to_dict(), ensure_ascii=False, indent=2), encoding='utf-8')
    temporary.replace(path)

def load(path):
    path = Path(path)
    result = Preset.from_dict(json.loads(path.read_text(encoding='utf-8-sig')))
    for obj in references(result):
        if obj.image and not Path(obj.image).is_absolute():
            obj.image = str((path.parent / obj.image).resolve())
    return result

def export_zip(preset, path):
    preset = copy.deepcopy(preset)
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as archive:
        for index, obj in enumerate(references(preset)):
            if obj.image:
                original = Path(obj.image)
                obj.image = f'images/{index}{original.suffix.lower()}'
                archive.write(original, obj.image)
        archive.writestr('preset.json', json.dumps(preset.to_dict(), ensure_ascii=False, indent=2))

def import_zip(path, destination):
    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        if len(infos) > 500 or sum(i.file_size for i in infos) > 100_000_000:
            raise ValueError(tr('프리셋 ZIP이 너무 큽니다.'))
        names = set()
        for info in infos:
            name = PurePosixPath(info.filename)
            if name.is_absolute() or '..' in name.parts or '\\' in info.filename or ':' in info.filename or info.filename.casefold() in names or (info.external_attr >> 16) & 0o170000 == 0o120000:
                raise ValueError(tr('안전하지 않은 ZIP 경로입니다.'))
            for part in name.parts:
                if part.endswith((' ', '.')) or any(c in part for c in '<>"|?*') or part.split('.')[0].upper() in {'CON', 'PRN', 'AUX', 'NUL', *(f'COM{i}' for i in range(1, 10)), *(f'LPT{i}' for i in range(1, 10))}:
                    raise ValueError(tr('Windows에서 안전하지 않은 ZIP 경로입니다.'))
            names.add(info.filename.casefold())
        if 'preset.json' not in names:
            raise ValueError(tr('ZIP에 preset.json이 없습니다.'))
        preset = Preset.from_dict(json.loads(archive.read('preset.json')))
        for obj in references(preset):
            if obj.image and (obj.image.casefold() not in names or not obj.image.startswith('images/')):
                raise ValueError(tr('ZIP 내부 이미지 참조가 잘못되었습니다.'))
        target = Path(destination) / str(uuid.uuid4())
        target.mkdir(parents=True)
        for info in infos:
            if not info.is_dir():
                output = target / info.filename
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_bytes(archive.read(info))
        return load(target / 'preset.json')
