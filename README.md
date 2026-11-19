# CFC 영상 데이터 추출기

Windows 10/11용 한국어 PySide6 데스크톱 프로그램입니다. MP4/MKV에서 기준 이미지의 등장 이벤트를 감지하고, 지정한 영상 시간만큼 지난 프레임에서 OCR과 이미지 존재 여부를 추출합니다. 분석 중 인터넷을 사용하거나 모델을 자동 다운로드하지 않습니다.

## 설치와 실행

Windows x64, Python 3.12를 기준으로 개발합니다. PowerShell에서:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

고정 버전: PySide6 6.8.3, PyAV 14.2.0, OpenCV 4.11.0.86, NumPy 2.2.3, tesserocr 2.12.0, Pillow 13.0.0, PyInstaller 6.12.0, pytest 8.3.5. 실제 설치 조합은 `requirements-lock.txt`에 기록합니다. PyAV Windows wheel에 FFmpeg 라이브러리가 포함되므로 별도 ffmpeg.exe는 필요하지 않습니다. 첫 설치에는 패키지 다운로드가 필요하며, 이후 실행은 오프라인입니다. 다른 PC에 오프라인 설치하려면 동일한 Python/Windows 아키텍처에서 `pip download -r requirements.txt -d wheels`로 준비하고 `pip install --no-index --find-links wheels -r requirements.txt`로 설치합니다.

## OCR 엔진 준비

OCR은 Tesseract 5.5.3을 tesserocr로 직접 호출합니다. [tesserocr Windows wheel](https://pypi.org/project/tesserocr/2.12.0/)에 엔진과 DLL이 포함되므로 별도 Tesseract 설치나 GPU가 필요하지 않습니다. 언어별 모델은 별도로 준비합니다.

`resources/tessdata/`에 `eng.traineddata`, `kor.traineddata`, `jpn.traineddata`를 준비합니다. 포함된 준비 스크립트는 [공식 tessdata_fast](https://github.com/tesseract-ocr/tessdata_fast)의 4.1.0 태그에서 세 모델과 라이선스를 다운로드합니다. 이 명령만 최초 준비 시 네트워크를 사용하며 앱은 이를 자동 실행하지 않습니다.

```powershell
.\.venv\Scripts\python.exe tools\prepare_models.py
.\.venv\Scripts\python.exe main.py
```

모델을 수동 복사하여 완전히 오프라인으로 준비할 수도 있습니다. 외부 모델 폴더를 사용하려면 `$env:TESSDATA_PREFIX = 'D:\models\tessdata'`를 지정하세요. 언어 조합별 PyTessBaseAPI를 한 번 초기화해 작업 동안 재사용하며 이미지 버퍼만 매번 해제합니다. 작업 종료 시 엔진을 정리합니다. 언어 모델 누락은 결과 파일을 열기 전에 안내하며, 실행 중 인식 실패는 항목별 기본값과 로그로 처리합니다.

## 사용 순서

GUI 언어는 상단 **Language**에서 한국어·English·日本語 중 선택합니다. 화면 언어와 항목의 OCR 언어는 독립적이며, 언어를 바꿔도 사용자 입력값은 유지됩니다.

1. **영상 선택** 또는 미리보기 영역으로 파일 하나를 드래그 앤 드롭하여 MP4/MKV를 엽니다. 해상도, FPS, 길이를 확인하고 슬라이더·초 이동·이전/다음 프레임으로 위치를 조절합니다.
2. **이벤트 감지** 탭에서 PNG/JPG 기준 이미지를 선택합니다. 영상 위를 드래그하거나 X/Y/폭/높이를 입력합니다. 좌표는 화면 크기와 무관한 원본 픽셀 좌표입니다.
3. 임계값(기본 0.9), 탐색 간격(기본 0.2초), 지연(기본 0), 연속 미감지 시간(기본 0)을 설정합니다. 짧은 이벤트를 모두 검사하려면 간격을 0으로 지정합니다. 다중 스케일은 `0.8, 1, 1.2`처럼 입력합니다.
4. **추출 항목** 탭에서 OCR/이미지 항목을 추가합니다. 목록에서 항목을 선택하고 설정합니다. 이 탭에서 드래그하면 선택 항목의 영역이 바뀝니다. **항목 편집 적용**으로 목록 표시를 갱신합니다. 항목을 바꾸거나 분석·저장할 때도 편집 내용이 적용됩니다. 활성화를 끄면 해당 항목은 분석과 출력에서 제외됩니다. 위/아래로 출력 순서를 변경합니다.
5. **현재 프레임에서 감지 / 추출 테스트**로 감지 유사도, 항목별 값, TXT 한 줄을 로그에서 확인합니다. 이벤트 기준 이미지가 비어 있으면 이벤트 감지를 생략하고 항목 테스트를 수행합니다. 등록한 기준 이미지가 손상되거나 없으면 오류를 안내합니다. 전체 분석에는 이벤트 기준 이미지가 필요합니다. 테스트는 결과 파일을 변경하지 않습니다.
6. **프리셋 / 출력**에서 이름과 출력 폴더를 지정합니다. 공백이면 영상 폴더를 사용합니다. 여러 JSON 프리셋을 저장·로드·수정·삭제하고 ZIP으로 이미지와 함께 이동할 수 있습니다. 이름 필드 변경은 프리셋 내부 이름을 바꾸며, 파일 이름 변경은 다른 이름으로 저장을 사용합니다. 가져온 ZIP은 사용자 데이터 폴더의 고유 디렉터리에 저장됩니다.
7. **분석 시작**을 누릅니다. 기존 결과가 있으면 덮어쓰기를 확인합니다. 일시정지/재개/중단을 지원합니다. 설정은 시작 시 복사되어 분석 중 편집해도 진행 중 결과에 영향을 주지 않습니다.

프리셋 대화상자의 기본 위치는 소스 실행 시 프로젝트 루트의 `presets/`, EXE 실행 시 EXE 옆의 `presets/`입니다. 폴더는 프로그램 시작 시 생성하며 다른 위치도 선택할 수 있습니다. 기존 프리셋 저장은 원래 파일 위치를 유지합니다.



## 시간과 TXT 규칙

디코딩은 [PyAV의 PTS와 time_base](https://pyav.org/docs/stable/api/time.html)를 사용합니다. 스트림 시작 PTS를 0으로 정규화하며 시작 PTS가 없으면 첫 프레임 PTS를 사용합니다. FPS는 표시용이며 추출 시간 계산에 사용하지 않습니다. 누락되거나 역행하는 PTS는 추정하지 않고 오류로 처리합니다. 전체 영상을 메모리에 저장하지 않고 순차 디코딩합니다.

탐색 간격은 이벤트 감지에만 적용합니다. 예약 추출은 모든 디코딩 프레임의 PTS를 확인해 목표 이상인 첫 프레임에서 처리합니다. 대기 중에도 새 이벤트를 감지하며, 같은 프레임에 여러 예약이 있으면 이벤트 순서대로 각각 기록합니다. 마지막 프레임 이후 예약은 로그에 남기고 제외합니다.

미감지 안정화는 **재무장**을 지연합니다. 연속 미감지 시작부터 설정 시간 이상 지났을 때 감지 상태를 해제합니다. 신규 등장 자체는 즉시 확정하므로 이벤트 시점과 확정 시점은 동일합니다. 그 이벤트 PTS에 추출 지연을 더합니다. 영상 처음부터 이미지가 있으면 즉시 첫 이벤트입니다.

출력은 영상과 같은 이름의 `.txt`, UTF-8 BOM, 헤더 없음, 활성 항목 순서의 값 뒤에 실제 추출 PTS `HH:MM:SS.mmm`입니다. 구분자는 쉼표+공백이며 쉼표와 따옴표는 CSV 인용으로 보존합니다. **이벤트당 물리적 한 줄** 요구와 문자열 내부 줄바꿈 보존은 일반 CSV에서 충돌하므로, CR/LF는 문자 `\r`/`\n`으로 이스케이프합니다. Python에서 읽을 때 `csv.reader(..., skipinitialspace=True)`를 사용하세요. 각 기록 후 flush하여 중단 이전 결과를 보존합니다. 이벤트가 없어도 BOM이 있는 빈 TXT가 생성됩니다.

진행률은 영상 메타데이터의 길이 기준이므로 길이 정보가 부정확하거나 없으면 정확하지 않을 수 있습니다. 미리보기의 랜덤 이동은 키프레임 탐색 후 순차 디코딩하므로 긴 GOP에서는 지연될 수 있습니다. 모든 프레임의 이벤트 감지는 CPU 비용이 증가합니다.

## 빌드와 배포

```powershell
.\build.bat
```

의존성 설치 → 테스트 → PyInstaller onedir 빌드 순서입니다. 결과는 `dist/CFCVideoTextExtractor/CFCVideoTextExtractor.exe`입니다. EXE만 복사하지 말고 `_internal`을 포함한 **폴더 전체**를 배포하세요. Python이 없는 Windows x64 PC에서 실행하도록 Python·Qt·OpenCV·PyAV·Tesseract 라이브러리를 포함합니다. 언어 모델 포함 여부는 빌드 당시 `resources/tessdata/` 내용에 따릅니다. 모델을 포함하지 않으면 대상 PC에서 TESSDATA_PREFIX로 로컬 모델을 지정해야 합니다. 배포 전 실제 대상 Windows에서 검사하세요.

사용자 데이터와 진단 로그는 `%LOCALAPPDATA%/CFCVideoTextExtractor/`에 저장합니다. JSON 프리셋은 저장 대화상자에서 선택한 위치에 저장합니다. 실행 도중 쓰기 권한/잠금/디코딩 오류는 오류창과 로그로 안내합니다. 중단은 현재 OCR 호출이 종료된 후 반영될 수 있으며 OCR 제한시간은 항목당 30초입니다. 작업 중 창 닫기를 요청하면 중단하고, 종료가 끝난 뒤 다시 닫도록 안내합니다.

## 구조와 단계

| 단계 | 파일 | 역할 및 다음 연결 |
|---|---|---|
| 1–2 | `main.py`, `models/preset.py`, `services/configuration.py` | 진입점, 설정 타입·검증, 사용자 데이터 경로 |
| 3–4 | `core/video_reader.py`, `gui/video_preview.py` | PTS 영상 읽기, 미리보기, 화면/원본 좌표 변환 |
| 5–7 | `core/image_detector.py`, `core/event_detector.py`, `core/extraction_scheduler.py` | 스케일 매칭, 상승 에지, 독립 예약 |
| 8–9 | `gui/extraction_editor.py`, `core/ocr_engine.py`, `core/extraction_processor.py` | 동적 항목, 언어·전처리, 순서별 값 |
| 10–11 | `services/output_writer.py`, `services/preset_service.py` | TXT 이스케이프, JSON/ZIP 관리 |
| 12–13 | `gui/main_window.py`, `core/analysis_worker.py` | GUI 통합, 백그라운드 분석·테스트, 상태·오류 |
| 14 | `tests/` | 이벤트·예약·출력·프리셋·합성 영상·GUI 검증 |
| 15 | `build.bat`, `resources/` | Windows EXE와 선택적 OCR 포함 |

전체 코드는 위 소스 파일에 있습니다. `presets/example.json`은 OCR·이미지 혼합 예제입니다. 이미지 경로와 영역은 실제 영상에 맞춰 지정해야 합니다.

## 검증

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

검증 결과와 미검증 사항은 `VALIDATION.md`를 확인하세요. 자동 테스트는 합성 데이터로 동작 규칙을 확인하며 실제 사용자 영상의 인식 정확도를 보장하지 않습니다.

현재 작업 폴더에는 언어 모델과 Windows 빌드 결과가 준비되어 있습니다. `dist/CFCVideoTextExtractor/CFCVideoTextExtractor.exe`를 실행하면 됩니다. 소스와 EXE의 오프라인 자체 점검 결과는 `source-smoke.json`, `exe-smoke.json`에 있습니다. 자체 점검은 `--self-test 결과파일.json` 옵션으로 실행하며 GUI를 화면에 표시하지 않고 초기화·렌더링·모델 로드·OCR을 검사합니다.

## Output templates

Use the output formatting button to set a preset-wide template such as `{Name}: {Score}`. Field names must exactly match enabled extraction item names, including Korean or Japanese names. The dialog lists available fields. Use `{{` and `}}` for literal braces. Duplicate/empty names, unknown fields, invalid braces and format/conversion specifiers are rejected. Clear the template to restore the original ordered CSV output. With a template, its rendered result becomes one CSV field followed by the existing video timestamp. Image present/absent text and OCR fallback values remain available as field values. Templates are saved in JSON/ZIP presets; old presets default to an empty template. Unsupported old item formatting fields are discarded.

File and folder selection uses native Windows dialogs; their standard controls follow Windows language settings.
