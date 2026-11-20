"""Local GUI translations. User names, paths, OCR languages and output values are never translated."""
_language = 'ko'
_qt_translator = None
_font_families = {}
_rows = '''CFC 영상 데이터 추출기|CFC Video Data Extractor|CFC 動画データ抽出
MP4 / MKV 영상을 선택하세요|Select an MP4 / MKV video|MP4 / MKV 動画を選択してください
영상 선택|Open video|動画を選択
이전 프레임|Previous frame|前のフレーム
다음 프레임|Next frame|次のフレーム
초로 이동|Go to seconds|指定秒へ移動
현재 프레임에서 감지 / 추출 테스트|Test detection / extraction on current frame|現在のフレームで検出・抽出テスト
분석 시작|Start analysis|解析開始
일시정지|Pause|一時停止
재개|Resume|再開
분석 중단|Stop analysis|解析中止
준비|Ready|準備完了
오류|Error|エラー
오류: |Error: |エラー: 
작업 오류|Operation error|操作エラー
이벤트 기준 이미지|Event reference image|イベント基準画像
원본 좌표|Original coordinates|元動画の座標
유사도 임계값|Similarity threshold|類似度しきい値
스케일 (예: 0.8, 1, 1.2)|Scales (e.g. 0.8, 1, 1.2)|倍率 (例: 0.8, 1, 1.2)
탐색 간격 (초, 0=모든 프레임)|Scan interval (seconds, 0=all frames)|検出間隔 (秒、0=全フレーム)
추출 지연 (초)|Extraction delay (seconds)|抽出遅延 (秒)
연속 미감지 시간 (초)|Continuous absence (seconds)|連続未検出時間 (秒)
이벤트 감지|Event detection|イベント検出
추출 항목|Extraction items|抽出項目
항목 추가|Add item|項目追加
삭제|Delete|削除
위로|Move up|上へ
아래로|Move down|下へ
항목 편집 적용|Apply item changes|項目の変更を適用
출력 형식 변경|Output formatting|出力形式を変更
출력 형식 사용법|Output formatting help|出力形式の使い方
프리셋 이름|Preset name|プリセット名
출력 폴더 (공백=영상 폴더)|Output folder (empty=video folder)|出力フォルダー (空欄=動画フォルダー)
출력 폴더 선택|Choose output folder|出力フォルダーを選択
출력 폴더|Output folder|出力フォルダー
새 프리셋|New preset|新規プリセット
프리셋 불러오기|Load preset|プリセットを読み込む
저장 / 이름 변경 반영|Save / apply name|保存・名前を反映
다른 이름으로 저장|Save as|名前を付けて保存
현재 프리셋 삭제|Delete current preset|現在のプリセットを削除
ZIP 내보내기|Export ZIP|ZIP エクスポート
ZIP 가져오기|Import ZIP|ZIP インポート
프리셋 / 출력|Presets / output|プリセット・出力
추출 항목 추가|Add extraction item|抽出項目を追加
유형|Type|種類
문자열 (OCR)|Text (OCR)|文字列 (OCR)
문자열|Text|文字列
이미지 존재 여부|Image presence|画像の有無
항목 {0}|Item {0}|項目 {0}
영상 (*.mkv *.mp4)|Video (*.mkv *.mp4)|動画 (*.mkv *.mp4)
먼저 영상을 선택하세요.|Select a video first.|先に動画を選択してください。
먼저 추출 항목을 선택하세요.|Select an extraction item first.|先に抽出項目を選択してください。
활성화된 추출 항목이 없습니다.|No extraction items are enabled.|有効な抽出項目がありません。
덮어쓰기 확인|Confirm overwrite|上書きの確認
일시정지 요청|Pause requested|一時停止を要求しました
분석 재개|Analysis resumed|解析を再開しました
프리셋 저장|Save preset|プリセットを保存
프리셋 저장: {0}|Preset saved: {0}|プリセットを保存しました: {0}
프리셋 삭제|Delete preset|プリセットを削除
현재 JSON 프리셋을 삭제할까요?|Delete the current JSON preset?|現在の JSON プリセットを削除しますか？
이미지 선택|Choose image|画像を選択
기준 이미지|Reference image|基準画像
이미지 (*.png *.jpg *.jpeg)|Images (*.png *.jpg *.jpeg)|画像 (*.png *.jpg *.jpeg)
폭|Width|幅
높이|Height|高さ
활성화|Enabled|有効
이름|Name|名前
사용|Use|使用
유사도|Similarity|類似度
스케일 (쉼표 구분)|Scales (comma separated)|倍率 (カンマ区切り)
이미지 존재 시 출력|Text when present|画像がある場合の出力
이미지 없음 시 출력|Text when absent|画像がない場合の出力
OCR 언어|OCR language|OCR 言語
실패 기본값|Fallback text|失敗時の出力
확대 배율|Zoom factor|拡大倍率
대비|Contrast|コントラスト
전처리|Preprocessing|前処理
그레이스케일|Grayscale|グレースケール
이진화|Binarization|二値化
노이즈 제거|Denoise|ノイズ除去
확인|OK|確認
취소|Cancel|キャンセル
이벤트 기준 미등록: 이벤트 감지 생략|No event reference: event detection skipped|イベント基準未登録: イベント検出を省略
이벤트 감지: {0} (유사도 {1:.4f})|Event detected: {0} (similarity {1:.4f})|イベント検出: {0} (類似度 {1:.4f})
TXT 미리보기: |TXT preview: |TXT プレビュー: 
감지|Detected|検出
기록|Written|記録
대기|Pending|待機
OCR 실패 [{0}]: {1}; 기본값 사용|OCR failed [{0}]: {1}; using fallback|OCR 失敗 [{0}]: {1}; 既定値を使用
OCR 언어 모델이 없습니다: {0}|Missing OCR language models: {0}|OCR 言語モデルがありません: {0}
OCR 엔진 초기화 실패 ({0}): {1}|OCR initialization failed ({0}): {1}|OCR 初期化失敗 ({0}): {1}
OCR 인식에 실패했거나 제한시간을 초과했습니다.|OCR failed or timed out.|OCR が失敗したか制限時間を超えました。
Windows에서 안전하지 않은 ZIP 경로입니다.|Unsafe Windows ZIP path.|Windows で安全ではない ZIP パスです。
ZIP 내부 이미지 참조가 잘못되었습니다.|Invalid image reference inside ZIP.|ZIP 内の画像参照が無効です。
ZIP에 preset.json이 없습니다.|ZIP does not contain preset.json.|ZIP に preset.json がありません。
{0:.3f}초 감지 상태: {1}|{0:.3f}s detection state: {1}|{0:.3f}秒 検出状態: {1}
기록 #{0}: {1}|Written #{0}: {1}|記録 #{0}: {1}
기준 이미지를 읽을 수 없습니다: {0}|Cannot read reference image: {0}|基準画像を読み込めません: {0}
모든 스케일의 기준 이미지가 탐색 영역보다 큽니다.|Reference images at all scales exceed the search region.|すべての倍率で基準画像が検索領域より大きくなっています。
분석 실패|Analysis failed|解析失敗
분석 실패: {0}|Analysis failed: {0}|解析失敗: {0}
분석 작업이 종료되었습니다.|Analysis task finished.|解析処理が終了しました。
빈 영상입니다.|The video is empty.|動画が空です。
사용자가 분석을 중단했습니다. 기존 결과는 보존됩니다.|Analysis stopped by user. Existing results are preserved.|解析を中止しました。記録済みの結果は保持されます。
안전하지 않은 ZIP 경로입니다.|Unsafe ZIP path.|安全ではない ZIP パスです。
영상 타임스탬프가 잘못되었거나 역행합니다.|Invalid or decreasing video timestamps.|動画のタイムスタンプが無効または逆行しています。
영상 프레임의 PTS가 없습니다. 정확한 시간 분석이 불가능합니다.|Video frame has no PTS; accurate timing is unavailable.|フレームに PTS がないため正確な時間解析ができません。
영상에 디코딩 가능한 프레임이 없습니다.|No decodable frames in the video.|動画にデコード可能なフレームがありません。
영상을 열 수 없습니다: {0}|Cannot open video: {0}|動画を開けません: {0}
이미지가 손상되었습니다: {0}|Invalid image: {0}|画像が破損しています: {0}
이벤트 #{0}: {1:.3f}초 → {2:.3f}초 예약|Event #{0}: {1:.3f}s → scheduled at {2:.3f}s|イベント #{0}: {1:.3f}秒 → {2:.3f}秒に予約
이벤트 #{0}: 영상 종료 이후 예약({1:.3f}초), 기록 제외|Event #{0}: target {1:.3f}s is beyond video end; skipped|イベント #{0}: 予約時刻 {1:.3f}秒は動画終了後のため記録を省略
프리셋 ZIP이 너무 큽니다.|Preset ZIP is too large.|プリセット ZIP が大きすぎます。
해당 시점의 프레임을 읽을 수 없습니다.|Cannot read a frame at this time.|指定時刻のフレームを読み込めません。
영역 좌표는 정수여야 합니다.|Region coordinates must be integers.|領域座標は整数で指定してください。
지원하지 않는 프리셋 버전입니다.|Unsupported preset version.|未対応のプリセットバージョンです。
시간은 0 이상의 유한한 값이어야 합니다.|Time must be a finite nonnegative value.|時間は0以上の有限値で指定してください。
유사도는 0~1이어야 합니다.|Similarity must be between 0 and 1.|類似度は0～1で指定してください。
스케일은 0 초과 10 이하입니다.|Scale must be greater than 0 and at most 10.|倍率は0より大きく10以下で指定してください。
항목 ID가 중복되었습니다.|Duplicate item IDs.|項目IDが重複しています。
알 수 없는 항목 유형입니다.|Unknown item type.|不明な項目の種類です。
OCR 확대/대비는 0.1~10이어야 합니다.|OCR zoom/contrast must be between 0.1 and 10.|OCR 拡大倍率・コントラストは0.1～10で指定してください。
'''  # Three columns: source Korean, English, Japanese.
CATALOG = {parts[0]: {'en': parts[1], 'ja': parts[2]} for line in _rows.splitlines() if len(parts := line.split('|')) == 3}
CATALOG.update({
    '{0}\n기존 결과를 덮어쓸까요?': {'en': '{0}\nOverwrite existing results?', 'ja': '{0}\n既存の結果を上書きしますか？'},
    '이미지가 없습니다. 해당 이미지 선택 버튼으로 경로를 다시 지정하세요.\n': {'en': 'Images are missing. Use Choose image to update the paths.\n', 'ja': '画像が見つかりません。画像選択ボタンでパスを指定し直してください。\n'},
    '작업 종료를 기다리는 중입니다. 종료 후 창을 다시 닫아 주세요.': {'en': 'Waiting for the task to stop. Close the window again after it finishes.', 'ja': '処理の終了を待っています。終了後にもう一度ウィンドウを閉じてください。'},
    '{0} / {1} | 감지 {2} | 기록 {3} | 대기 {4}': {'en': '{0} / {1} | Detected {2} | Written {3} | Pending {4}', 'ja': '{0} / {1} | 検出 {2} | 記録 {3} | 待機 {4}'},
    '미감지 안정화는 재감지 준비만 늦춥니다.\n새 감지는 즉시 이벤트가 되며, 그 PTS부터 지연을 계산합니다.\n드래그 영역은 현재 탭의 선택 항목에 적용됩니다.': {
        'en': 'Absence stabilization delays rearming only.\nNew detections trigger immediately; delay starts at that PTS.\nDragging sets the region for the current tab / selected item.',
        'ja': '未検出の安定化は再検出の準備のみを遅らせます。\n新規検出は即時イベントとなり、その PTS から遅延を計算します。\nドラッグは現在のタブ・選択項目の領域に適用されます。'},
})

def get_language() -> str:
    return _language

def set_language(language: str):
    global _language, _qt_translator
    if language not in ('ko', 'en', 'ja'):
        raise ValueError('Unsupported language')
    _language = language
    from PySide6.QtCore import QCoreApplication, QLibraryInfo, QTranslator
    app = QCoreApplication.instance()
    if app:
        if _qt_translator:
            app.removeTranslator(_qt_translator)
        _qt_translator = QTranslator(app)
        if _qt_translator.load('qtbase_' + language, QLibraryInfo.path(QLibraryInfo.TranslationsPath)):
            app.installTranslator(_qt_translator)
        if hasattr(app, 'setFont'):
            from pathlib import Path
            from PySide6.QtGui import QFont, QFontDatabase
            filename = 'msgothic.ttc' if language == 'ja' else 'malgun.ttf'
            font = Path('C:/Windows/Fonts') / filename
            if font.is_file():
                if filename not in _font_families:
                    font_id = QFontDatabase.addApplicationFont(str(font))
                    _font_families[filename] = QFontDatabase.applicationFontFamilies(font_id)
                if _font_families[filename]:
                    app.setFont(QFont(_font_families[filename][0], 9))

def tr(source: str) -> str:
    return CATALOG.get(source, {}).get(_language, source)

def localize_widgets(window):
    from PySide6.QtWidgets import QLabel, QAbstractButton, QComboBox, QTabWidget
    reverse = {value: key for key, translations in CATALOG.items() for value in translations.values()}
    def translate(text):
        return tr(reverse.get(text, text))
    window.setWindowTitle(translate(window.windowTitle()))
    for widget in window.findChildren(QLabel) + window.findChildren(QAbstractButton):
        text = widget.text()
        if text in CATALOG or text in reverse:
            widget.setText(translate(text))
    for combo in window.findChildren(QComboBox):
        if not combo.isEditable():
            combo.blockSignals(True)
            for index in range(combo.count()):
                combo.setItemText(index, translate(combo.itemText(index)))
            combo.blockSignals(False)
    for tabs in window.findChildren(QTabWidget):
        for index in range(tabs.count()):
            tabs.setTabText(index, translate(tabs.tabText(index)))

CATALOG.update({
    'Output formatting': {'ko': '\ucd9c\ub825 \ud615\uc2dd \ubcc0\uacbd', 'ja': '\u51fa\u529b\u5f62\u5f0f\u3092\u5909\u66f4'},
    'Template (empty=original output)': {'ko': '\ud15c\ud50c\ub9bf (\ube48 \uac12=\uae30\uc874 \ucd9c\ub825)', 'ja': '\u30c6\u30f3\u30d7\u30ec\u30fc\u30c8 (\u7a7a\u6b04=\u5143\u306e\u51fa\u529b)'},
    'Available fields': {'ko': '\uc0ac\uc6a9 \uac00\ub2a5\ud55c \ud544\ub4dc', 'ja': '\u4f7f\u7528\u53ef\u80fd\u306a\u30d5\u30a3\u30fc\u30eb\u30c9'},
    'Error': {'ko': '\uc624\ub958', 'ja': '\u30a8\u30e9\u30fc'},
    'Invalid template field or braces.': {'ko': '\ud15c\ud50c\ub9bf \ud544\ub4dc \uc774\ub984 \ub610\ub294 \uc911\uad04\ud638\ub97c \ud655\uc778\ud558\uc138\uc694.', 'ja': '\u30d5\u30a3\u30fc\u30eb\u30c9\u540d\u307e\u305f\u306f\u62ec\u5f27\u3092\u78ba\u8a8d\u3057\u3066\u304f\u3060\u3055\u3044\u3002'},
    'Template requires unique, nonempty item names.': {'ko': '\ud15c\ud50c\ub9bf \uc0ac\uc6a9 \uc2dc \ud56d\ubaa9 \uc774\ub984\uc740 \ube44\uc5b4 \uc788\uac70\ub098 \uc911\ubcf5\ub420 \uc218 \uc5c6\uc2b5\ub2c8\ub2e4.', 'ja': '\u9805\u76ee\u540d\u306f\u7a7a\u6b04\u30fb\u91cd\u8907\u306b\u3067\u304d\u307e\u305b\u3093\u3002'},
})
