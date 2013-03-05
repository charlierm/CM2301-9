import os, re, subprocess, threading
from ffprobe import *

class FFMpegException(Exception):
    pass

class Converter(object):
    input_file = None
    output_file = None
    ffmpeg_path = None
    container = None
    video_codec = None
    audio_codec = None
    _progress = None
    _is_started = False
    _process = None
    _length = None
    _dimensions = {}

    def __init__(self, input_path, output_path, ffmpeg_path=None):
        """
        Converter constructer, must be initialized with input path video.
        """
        if not ffmpeg_path:
            path = '/usr/local/bin/ffmpeg'
        else:
            path = ffmpeg_path
        if os.path.exists(path):
            self.ffmpeg_path = path
        else:
            raise FFMpegException('ffmpeg binary not found: %s' % (path))
        
        if os.path.exists(input_path):
            self.input_file = input_path
        else:
            raise FFMpegException('Input file does not exist: %s' % (input_path))
        
        self.output_file = output_path

    def set_container(self, container):
        """
        Sets the container format. e.g mp4
        """
        self.container = container

    def set_video_codec(self, video_codec):
        """
        Sets the output video codec.
        
        @param VideoCodec The constant codec 
        """
        self.video_codec = video_codec

    def set_audio_codec(self, audio_codec):
        """
        Set the output audio codec.
        
        @param VideoCodec The codec to be used.
        """
        self.audio_codec = audio_codec
        
    def set_dimensions(self, height=None, width=None):
        """
        Sets either the height, width or both for the encoding.
        
        If using certain VideoCodec then neither of these should be an odd number.
        
        @param height The height in pixels.
        @param width The width in pixels.  
        """
        if height == None and width == None:
             raise TypeError("No dimensions given")
        else:
             self._dimensions = {'width': width, 'height': height}
         

    def start(self):
        """
        Starts the current conversion task the background.
        """
        print ' '.join(self._parse_options())
        thread = threading.Thread(target=self.__conversion)
        thread.start()

    def cancel(self):
        """
        Cancels the current conversion task.
        """
        if self._is_started:
            self._process.kill()
            self._process = None
            self._is_started = False
            self._progress = 0
            
        else:
            raise FFMpegException('No conversion to kill')
        

    def __to_decimal(self, hms):
        """
        Converts the supplied [h,m,s] list to
        decimal seconds.
        
        @param list List of hms
        returns float Returns total seconds. 
        """
        h = float(hms[0]) * 3600
        m = float(hms[1]) * 60
        s = float(hms[2])
        return h+m+s

    def get_duration(self):
        """
        Returns the duration of the video in seconds as a decimal.
        
        May be better to use FFProbe.
        """
        p = subprocess.Popen(['/usr/local/bin/ffmpeg', '-i', self.input_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = p.stderr.read()
        regex = re.compile('Duration: (\d\d):(\d\d):(\d\d(\.\d\d)?)')
        tmp = regex.findall(output)
        return self.__to_decimal(tmp[0])

    def __conversion(self):
        """
        This method is run by the thread, it executes the ffmpeg process
        and captures the output.
        """
        self._is_started = True
        self._length = self.get_duration()
        
        self._process = subprocess.Popen(self._parse_options(),
                                         stdout=subprocess.PIPE, 
                                         stderr=subprocess.PIPE)

        buf = ''
        total_output = ''
        pat = re.compile(r'time=([0-9.:]+) ')

        while True:
            fd = self._process.stderr
            ret = fd.read(10)

            if not ret:
                break

            total_output += ret
            buf += ret

            if '\r' in buf:
                line, buf = buf.split('\r', 1)
                tmp = pat.findall(line)
                parts = tmp[0].split(':')
                progress = self.__to_decimal(parts)
                percent = (progress/self._length)*100
                self._progress = round(percent, 2)
                
                
    def _parse_options(self):
        """
        Checks the current config for the encoding and outputs the 
        correct commands for ffmpeg.
        """
        video = []
        if self.container is ContainerFormat.WEBM:
            video = ['-codec:v', VideoCodec.VP8, 
                    '-quality', 'good', 
                    '-cpu-used', '0',
                    '-b:v', '500k',
                    '-qmin', '10',
                    '-qmax', '42',
                    '-vf', 'scale=-1:480'
                    ]
        elif self.container is ContainerFormat.MP4:
            video = ['-codec:v', VideoCodec.H264,
                    '-vprofile', 'high',
                    '-preset', 'slow',
                    '-b:v', '500k',
                    '-maxrate', '500k',
                    '-bufsize', '1000k',
                    '-vf', 'scale=-1:480'
                    ]
            
        audio = ['-codec:a', self.audio_codec,
                 '-b:a', '128k'
                 ]
        
        cmds = [self.ffmpeg_path, '-i', self.input_file] + video + audio + ['-y', self.output_file]
        
        return cmds
    
    
    def _scale(self):
        ratio = MIN( maxWidth / width, maxHeight/ height )
        width = ratio * width
        height = ratio * height
        

    @property
    def progress(self):
        """
        The current progress of the encoding, as a percentage.
        
        @return float The progress ffmpeg as a percentage.
        """
        if (self._progress is None
            and self._is_started is False):
            raise FFMpegException("Conversion not started")
        else:
            return self._progress
        
    @property
    def probe(self):
        """
        Returns information about the current file using ffprobe.
        @return FFProbe Returns an ffprobe for the current file.
        """
        return FFProbe(self.input_file)

class ContainerFormat(object):
    """
    Container format class
    """
    OGG = 'ogg'
    AVI = 'avi'
    MKV = 'matroska'
    WEBM = 'webm'
    FLV = 'flv'
    MOV = 'mov'
    MP4 = 'mp4'

class VideoCodec(object):
    """
    Collection of VideoCodec for ffmpeg.
    """
    THEORA = 'libtheora'
    H264 = 'libx264'
    FLV = 'flv'
    VP8 = 'libvpx'
    H263 = 'h263'
    DIVX = 'mpeg4'
    
class AudioCodec(object):
    """
    Collection of audio codecs for ffmpeg.
    """
    AAC = 'libfaac'
    VORBIS = 'libvorbis'
    MP3 = 'libmp3lame'
    MP2 = 'MP2'
    