# 구현 검증 기록

검증 환경: Windows 11 x64, Python 3.12.1, 프로젝트 `.venv`, CPU 실행.

자동 테스트 명령:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

현재 63개 테스트가 통과했습니다. 테스트 소스는 `tests/test_core.py`, `tests/test_video_gui.py`, `tests/test_integration.py`, `tests/test_requested_changes.py`입니다.

| 범위 | 실행 결과 |
|---|---|
| 첫 프레임 이벤트, 지속 감지 중복 방지, 재등장, 미감지 안정화 | 통과 |
| 지연 0/양수, 목표 이후 첫 프레임, 중첩 예약, 영상 끝 이후 예약 | 통과 |
| 중단 이전 TXT 보존, BOM, 쉼표·따옴표·줄바꿈 처리, 타임스탬프 반올림 | 통과 |
| OCR/이미지 혼합, 비활성화 제외, 순서 변경, OCR 실패 기본값 | 통과 |
| JSON 복원·독립성·수정·삭제, 이미지 포함 ZIP 왕복 | 통과 |
| ZIP 절대 경로·상위 경로·Windows 경로 차단 | 통과 |
| 실제 인코딩한 합성 H.264 MP4/MKV의 VFR PTS와 탐색 | 통과 |
| 합성 영상 → 템플릿 이벤트 → 예약 → 이미지 결과 TXT 전체 경로 | 통과 |
| Qt offscreen GUI 생성·항목 순서·영역 편집·이전/다음 프레임 | 통과 |
| 설정 스냅샷, 일시정지 중 체크포인트 대기와 중단 해제 | 통과 |
| 100,000개 프레임 메타데이터 순차 처리의 Python 메모리 | 추가 메모리 1MB 미만 테스트 통과 |
| 영어·한국어·일본어 모델 로드 및 동일 엔진 재사용 | 통과 |
| 실제 한국어 `안녕하세요`, 일본어 `こんにちは` 렌더링 OCR | 통과 |
| 손상된 영상, 없는 OCR 모델, 잘못된 프리셋 | 통과 |

메모리 테스트는 작은 메타데이터 생성기의 지속 저장 여부를 확인합니다. 실제 수십 시간 고해상도 영상의 프로세스 전체 RSS나 디코더 네이티브 메모리를 측정한 결과는 아닙니다.

소스 실행 자체 점검:

```powershell
.\.venv\Scripts\python.exe main.py --self-test source-smoke.json
```

GUI 생성, 한국어 글꼴 렌더링, PyAV/OpenCV/Tesseract 가져오기, 세 언어 모델 초기화, 영어 OCR `HELLO 123`을 확인했습니다. 결과는 `source-smoke.json`, 화면은 `source-smoke.png`입니다. 화면은 offscreen으로 확인했으며 실제 사용자 마우스로 모든 대화상자를 조작한 검증은 아닙니다.

Windows EXE도 실제 생성했습니다. 한국어·영어·일본어 모델을 포함하며 다음 명령으로 같은 점검에 통과했습니다.

```powershell
& '.\dist\CFCVideoTextExtractor\CFCVideoTextExtractor.exe' --self-test "$PWD\exe-smoke.json"
```

결과는 `exe-smoke.json`의 `success: true`, 화면은 `exe-smoke.png`입니다. 이 점검은 현재 개발 PC에서 수행했으므로 Python이 없는 별도 클린 PC 검증과는 구분합니다. PyInstaller의 선택적·다른 OS용 모듈 누락 경고는 생성되었으나 이 실행 경로에서는 오류가 없었습니다.

검증하지 않은 범위: 사용자 실제 영상의 인식 정확도, 모든 MKV/MP4 코덱, Windows 10 별도 PC, Python 미설치 클린 PC, 수십 시간 실영상 부하, 물리 디스크 장애·타 프로그램의 파일 잠금 재현. 해당 오류에 대한 예외 처리는 구현했으나 모든 외부 조건을 재현한 것은 아닙니다.

## 2026-11-19 변경 및 영향 검증

기존 32개 테스트와 추가 19개 테스트를 실행해 **51 passed**를 확인했습니다. 추가 검증은 다음을 포함합니다.

- 소스/EXE 위치 기준 presets 폴더 생성과 JSON 대화상자 기본 경로
- 사용자 지정 이미지 존재/없음 문구와 빈 문자열, 기본 True/False 출력 유지
- 정규식 숫자 추출, 날짜 캡처 재배치, 이름 있는 그룹, 미일치, 빈 패턴, 잘못된 패턴/그룹 참조 거부
- 새 필드 없는 기존 프리셋 복원, 새 필드 JSON/ZIP 왕복
- 실제 Qt drop 이벤트로 MP4 등록, 폴더/원격 URL/복수 파일/지원하지 않는 형식 거부
- 이벤트 기준 미등록 테스트의 결과 생성과 전체 분석의 기준 이미지 필수 조건 유지
- 한국어/영어/일본어 전환 시 버튼·탭·도움말 번역, 사용자 편집값과 기준 이미지 미리보기 보존
- 잘못된 출력 형식의 대화상자 적용 거부 및 GUI 번역 카탈로그 누락 검사

세 언어 화면을 Qt offscreen으로 렌더링해 `ui-ko.png`, `ui-en.png`, `ui-ja.png`에 저장했습니다. 일본어는 Windows MS Gothic, 한국어/영어는 맑은 고딕을 사용해 글리프 누락을 피합니다. 실제 마우스를 이용한 모든 대화상자 수동 검증과는 구분합니다.

영향 범위: 출력 변환은 항목의 추출값에만 적용하고 TXT 기록기는 변경하지 않았습니다. 새 필드는 기본값을 갖는 추가 필드로 도입해 기존 프리셋을 읽을 수 있습니다. 전체 분석의 이벤트/PTS/예약/CSV 처리 규칙은 유지하고, 테스트에서만 이벤트 기준 미등록을 허용합니다. GUI 언어와 OCR 언어 및 사용자 출력값은 서로 독립적입니다. 프리셋 기본 경로 이외의 로그/ZIP 가져오기 데이터 경로는 유지합니다.

변경 파일:

| 파일 | 내용 |
|---|---|
| `requirements.md`, `README.md`, `VALIDATION.md` | 요구사항 충돌 정리, 사용법, 영향 및 검증 기록 |
| `models/preset.py` | 이미지 출력 문구, 항목별 정규식 설정 및 검증 |
| `services/configuration.py` | 실행 위치 기준 presets 디렉터리 생성 |
| `services/text_format.py` (추가) | 정규식 검증과 값 변환 |
| `services/i18n.py` (추가) | 세 언어 카탈로그, Qt 표준 대화상자 번역, 글꼴 선택 |
| `services/preset_service.py` | 프리셋 오류 메시지 다국어 적용 |
| `gui/main_window.py` | 기본 프리셋 경로, 출력 형식/도움말/Language 버튼, 테스트 조건, 공통 영상 로딩 |
| `gui/extraction_editor.py` | 이미지 출력 문구 입력, 편집값 복원·저장, 다국어 레이블 |
| `gui/output_format_dialog.py` (추가) | 정규식 편집과 세 언어 예시 도움말 |
| `gui/video_preview.py` | 지원하는 로컬 영상 드래그 앤 드롭 |
| `gui/application.py` | 기본 한국어와 글꼴 설정 연결 |
| `core/extraction_processor.py` | 사용자 문구·정규식 적용, 테스트용 이벤트 검증 옵션 |
| `core/analysis_worker.py`, `core/image_detector.py`, `core/ocr_engine.py`, `core/video_reader.py` | 상태·오류 메시지 번역 연결; 분석 규칙은 유지 |
| `tests/test_requested_changes.py` (추가) | 추가 기능 및 기존 동작 호환성 회귀 테스트 |

Windows EXE를 최신 소스로 다시 빌드했고 자체 점검의 `success: true`를 확인했습니다. EXE 옆 `presets/` 폴더 생성도 확인했습니다. 실행 파일은 `dist/CFCVideoTextExtractor/`의 최신 빌드를 사용해야 합니다.

## Latest template/native-dialog revision

53 tests passed. Removed item search/replacement processing, associated help UI and translations. Output formatting is now a preset-wide template whose fields exactly reference enabled extraction item names. The default empty template retains the original output. A nonempty template is emitted as one CSV field followed by the existing PTS timestamp. Template validation runs before opening the result file. Existing presets load with an empty template and unsupported old item fields are discarded. Native Windows file/folder dialogs are restored (their controls use the OS language).

Changed files: requirements.md, README.md, VALIDATION.md; models/preset.py; services/text_format.py, services/output_writer.py, services/i18n.py; gui/main_window.py, gui/extraction_editor.py, gui/output_format_dialog.py; core/analysis_worker.py, core/extraction_processor.py; tests/test_requested_changes.py.

Verified: item-name lookup including spaces and dots, braces escaping, duplicate/missing fields, empty-template legacy CSV, template CSV escaping and timestamp, JSON/ZIP roundtrip, removal of help button, native-dialog default options. Existing event scheduling, OCR, video decoding and localization regressions also pass. Native Windows dialogs were verified through their invocation options; full manual OS dialog interaction was not performed. Earlier dated notes describe historical behavior superseded by this revision.

## 2026-11-20 Language persistence

63 tests passed, including ten language-settings cases: missing/corrupt/non-object/unsupported settings, Korean/English/Japanese startup restoration, dialog save and cancellation, preservation of unrelated settings. Tests use an isolated settings folder and do not modify real user preferences.

Changed: services/configuration.py (atomic settings save and safe load), gui/application.py (restore on startup), services/i18n.py (current language accessor), gui/main_window.py (save accepted selection and preselect current language), tests/test_language_settings.py, README.md, requirements.md, VALIDATION.md. Existing extraction and preset behavior remains unchanged.
