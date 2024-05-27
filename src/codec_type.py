class CodecType:
    PCM_16BIT_16KHZ_MONO = 0
    PCM_8BIT_16KHZ_MONO = 1
    MU_LAW_16BIT_16KHZ_MONO = 10
    MU_LAW_8BIT_16KHZ_MONO = 11
    OPUS_16BIT_16KHZ_MONO = 20

    def __init__(self, codec_type=PCM_8BIT_16KHZ_MONO):
        self.codec_type = codec_type

    def set_codec_type(self, codec_type):
        self.codec_type = codec_type

    def get_codec_type(self):
        return self.codec_type

