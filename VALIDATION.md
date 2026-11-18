# 구현 검증 기록

검증 환경: Windows 11 x64, Python 3.12.1, 프로젝트 `.venv`, CPU 실행.

자동 테스트 명령:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

현재 32개 테스트가 통과했습니다. 테스트 소스는 `tests/test_core.py`, `tests/test_video_gui.py`, `tests/test_integration.py`입니다.

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
