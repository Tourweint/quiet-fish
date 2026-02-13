"""音频监控模块"""
import pyaudio
import math
from collections import deque


class AudioMonitor:
    def __init__(self, smooth_frames=30):
        self.pa = pyaudio.PyAudio()
        self.stream = self.pa.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=44100,
            input=True,
            frames_per_buffer=1024
        )
        self.volume_history = deque(maxlen=smooth_frames)
        self.current_volume = 0

    def get_volume(self):
        """获取当前麦克风音量 (0-100)"""
        try:
            data = self.stream.read(1024, exception_on_overflow=False)
            # 直接使用字节数据进行计算，避免转换为列表
            rms = math.sqrt(sum(b * b for b in data) / len(data))
            volume = min(100, int(rms / 50))
            self.volume_history.append(volume)
            self.current_volume = sum(self.volume_history) / len(self.volume_history)
            return self.current_volume
        except OSError:
            # 音频设备读取错误时返回默认值
            return 0

    def is_quiet(self, threshold):
        """判断是否安静"""
        return self.current_volume < threshold

    def close(self):
        """关闭音频流和 PyAudio"""
        try:
            self.stream.stop_stream()
            self.stream.close()
        except OSError:
            pass  # 流可能已经关闭
        finally:
            self.pa.terminate()
