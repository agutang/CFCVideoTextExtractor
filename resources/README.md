이 디렉터리는 EXE에 포함됩니다.

OCR 엔진은 tesserocr Windows wheel에 포함되며, 언어별 모델은 `tessdata/` 아래에 둡니다.
`tessdata/{eng,kor,jpn}.traineddata`와 라이선스 파일을 함께 포함합니다.
외부 모델 폴더는 TESSDATA_PREFIX 환경변수로 지정할 수 있습니다.
