"""音频监控模块"""
import pyaudio
import math
import struct
from collections import deque

from config import AUDIO_RMS_DIVISOR, AUDIO_MAX_VOLUME, AUDIO_BUFFER_SIZE, AUDIO_SAMPLE_RATE


class AudioMonitor:
    def __init__(self, smooth_frames=30):
        self.pa = pyaudio.PyAudio()
        
        # 查找可用的输入设备
        device_index = None
        for i in range(self.pa.get_device_count()):
            info = self.pa.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                print(f"[AudioMonitor] 找到音频输入设备: {info['name']} (索引: {i})")
                if device_index is None:
                    device_index = i
        
        try:
            self.stream = self.pa.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=AUDIO_SAMPLE_RATE,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=AUDIO_BUFFER_SIZE
            )
            print("[AudioMonitor] 音频流初始化成功")
        except Exception as e:
            print(f"[AudioMonitor] 警告: 无法打开音频流: {e}")
            self.stream = None
            
        self.volume_history = deque(maxlen=smooth_frames)
        self.current_volume = 0

    def get_volume(self):
        """获取当前麦克风音量 (0-100)"""
        if self.stream is None:
            return 0
            
        try:
            data = self.stream.read(AUDIO_BUFFER_SIZE, exception_on_overflow=False)
            
            # 将字节数据转换为16位有符号整数数组
            # 每个样本是2个字节（16位）
            count = len(data) // 2
            format_str = f"{count}h"  # h 表示有符号短整型（16位）
            samples = struct.unpack(format_str, data[:count * 2])
            
            # 计算 RMS（均方根）
            if len(samples) > 0:
                sum_squares = sum(sample * sample for sample in samples)
                rms = math.sqrt(sum_squares / len(samples))
            else:
                rms = 0
            
            # 将 RMS 映射到 0-100 范围
            # 调整除数使音量条更敏感（值越小越敏感）
            volume = min(AUDIO_MAX_VOLUME, int(rms / AUDIO_RMS_DIVISOR))
            
            self.volume_history.append(volume)
            self.current_volume = sum(self.volume_history) / len(self.volume_history)
            
            return self.current_volume
            
        except OSError as e:
            # 音频设备读取错误时返回默认值
            print(f"[AudioMonitor] 读取错误: {e}")
            return self.current_volume
        except Exception as e:
            print(f"[AudioMonitor] 未知错误: {e}")
            return self.current_volume

    def is_quiet(self, threshold):
        """判断是否安静"""
        return self.current_volume < threshold

    def close(self):
        """关闭音频流和 PyAudio"""
        try:
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
        except OSError:
            pass  # 流可能已经关闭
        finally:
            self.pa.terminate()
