import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
from fractions import Fraction
import av
import numpy as np
import pytest
from PySide6.QtWidgets import QApplication
from core.video_reader import VideoReader
from gui.main_window import MainWindow
from models.preset import Preset, ExtractionItem, Region

def make_video(path, pts):
    with av.open(str(path), 'w') as container:
        stream = container.add_stream('libx264', rate=25)
        stream.width, stream.height = 64, 48
        stream.pix_fmt = 'yuv420p'
        stream.time_base = Fraction(1, 1000)
        stream.codec_context.time_base = Fraction(1, 1000)
        for index, time in enumerate(pts):
            frame = av.VideoFrame.from_ndarray(np.full((48, 64, 3), index*20, dtype=np.uint8), format='bgr24')
            frame.pts, frame.time_base = time, Fraction(1, 1000)
            for packet in stream.encode(frame):
                container.mux(packet)
        for packet in stream.encode():
            container.mux(packet)

@pytest.mark.parametrize('extension', ['mp4', 'mkv'])
def test_video_vfr_pts_seek(tmp_path, extension):
    path = tmp_path/f'test.{extension}'
    make_video(path, [0, 40, 100, 160, 300, 500])
    with VideoReader(path) as reader:
        times = [time for time, _ in reader.frames()]
        assert times == pytest.approx([0, .04, .1, .16, .3, .5], abs=.001)
        assert reader.at(.11)[0] == pytest.approx(.16, abs=.001)
        assert reader.width == 64

def test_corrupt_video(tmp_path):
    path = tmp_path/'broken.mp4'
    path.write_bytes(b'broken')
    with pytest.raises(ValueError):
        VideoReader(path)

@pytest.fixture(scope='module')
def app():
    return QApplication.instance() or QApplication([])

def test_gui_item_order_region_and_snapshot(app):
    window = MainWindow()
    preset = Preset(items=[ExtractionItem(name='A'), ExtractionItem(name='B', kind='image')])
    window.populate(preset)
    window.move_item(1)
    assert [i.name for i in window.preset.items] == ['B', 'A']
    window.tabs.setCurrentIndex(1)
    window.region_selected(Region(3, 4, 20, 10))
    window.apply_item()
    assert window.preset.items[1].region == Region(3, 4, 20, 10)
    window.editor.enabled.setChecked(False)
    window.sync()
    assert not window.preset.items[1].enabled
    window.delete_item()
    assert [i.name for i in window.preset.items] == ['B']
    window.close()

def test_gui_exact_frame_navigation(app, tmp_path):
    path = tmp_path/'navigation.mkv'
    make_video(path, [0, 40, 100, 160, 300, 500])
    window = MainWindow()
    window.reader = VideoReader(path)
    window.show_frame(*window.reader.at(0))
    window.next_frame()
    assert window.current_time == pytest.approx(.04, abs=.001)
    window.next_frame()
    assert window.current_time == pytest.approx(.1, abs=.001)
    window.previous_frame()
    assert window.current_time == pytest.approx(.04, abs=.001)
    window.close()
