from saleae.analyzers import HighLevelAnalyzer, AnalyzerFrame

class Hla(HighLevelAnalyzer):
    result_types = {
        "data": { "format": "{{data.value}}" }
    }

    def __init__(self):
        self.spi_enable           = False
        self.is_first_byte        = False
        self.is_second_byte       = False
        self.transaction_start    = None
        self.current_command      = None
        self.last_argument        = None
        self.bank                 = 0b00

    def handle_enable(self, frame):
        self.spi_enable        = True
        self.is_first_byte     = True
        self.is_second_byte    = False
        self.current_command   = None
        self.transaction_start = frame.start_time

    def handle_disable(self, frame):
        self.spi_enable        = False
        self.is_first_byte     = False
        self.is_second_byte    = False
        self.current_command   = None
        self.transaction_start = None
        self.last_argument     = None

    def get_frame_data(self, frame):
        mosi = frame.data.get('mosi', [0])[0]
        miso = frame.data.get('miso', [0])[0]
        return mosi, miso

    OPCODES = {
        0b000: "RC", 0b001: "RB", 0b010: "WC", 0b011: "WB",
        0b100: "SB", 0b101: "CB", 0b111: "SR"
    }

    REGISTERS = {
        0b00: {
            0x00: "ERDPTL",     0x01: "ERDPTH",     0x02: "EWRPTL",     0x03: "EWRPTH",
            0x04: "ETXSTL",     0x05: "ETXSTH",     0x06: "ETXNDL",     0x07: "ETXNDH",
            0x08: "ERXSTL",     0x09: "ERXSTH",     0x0A: "ERXNDL",     0x0B: "ERXNDH",
            0x0C: "ERXRPTL",    0x0D: "ERXRDPTH",   0x0E: "ERXWRPTL",   0x0F: "ERXWRPTH",
            0x10: "EDMACSTL",   0x11: "EDMASTH",    0x12: "EDMANDL",    0x13: "EDMANDH",
            0x14: "EDMADSTL",   0x15: "EDMADSTH",   0x16: "EDMACSL",    0x17: "EDMACSH",
            0x1B: "EIE",        0x1C: "EIR",        0x1D: "ESTAT",      0x1E: "ECON2",
            0x1F: "ECON1"
        },
        0b01: {
            0x00: "EHT0",       0x01: "EHT1",       0x02: "EHT2",       0x03: "EHT3",
            0x04: "EHT4",       0x05: "EHT5",       0x06: "EHT6",       0x07: "EHT7",
            0x08: "EPMM0",      0x09: "EPMM1",      0x0A: "EPMM2",      0x0B: "EPMM3",
            0x0C: "EPMM4",      0x0D: "EPMM5",      0x0E: "EPMM6",      0x0F: "EPMM7",
            0x10: "EPMCSL",     0x11: "EPMCSH",     0x14: "EPMOL",      0x15: "EPMOH",
            0x18: "ERXFCON",    0x19: "EPKTCNT",    0x1B: "EIE",        0x1C: "EIR",
            0x1D: "ESTAT",      0x1E: "ECON2",      0x1F: "ECON1"
        },
        0b10: {
            0x00: "MACON1",     0x02: "MACON3",     0x03: "MACON4",     0x04: "MABBIPG",
            0x05: "MAIPGL",     0x06: "MAIPGH",     0x07: "MACLCON1",   0x08: "MACLCON2",
            0x09: "MAMXFLL",    0x0A: "MAMXFLH",    0x12: "MICMD",      0x13: "MIREGADR",
            0x15: "MIWRL",      0x16: "MIWRH",      0x17: "MIRDL",      0x18: "MIRDH",
            0x1B: "EIE",        0x1C: "EIR",        0x1D: "ESTAT",      0x1E: "ECON2",
            0x1F: "ECON1"
        },
        0b11: {
            0x00: "MAADR5",     0x01: "MAADR6",     0x02: "MAADR3",     0x03: "MAADR4",
            0x04: "MAADR1",     0x05: "MAADR2",     0x06: "EBSTSD",     0x07: "EBSTCON",
            0x08: "EBSTCSL",    0x09: "EBSTCSH",    0x0A: "MISTAT",     0x10: "EREVID",
            0x16: "ECOCON",     0x17: "EFLOCON",    0x18: "EPAUSL",     0x19: "EPAUSH",
            0x1B: "EIE",        0x1C: "EIR",        0x1D: "ESTAT",      0x1E: "ECON2",
            0x1F: "ECON1"
        }
    }

    def handle_result(self, frame):
        if not self.spi_enable:
            return None

        mosi, miso = self.get_frame_data(frame)

        if self.is_first_byte:
            self.is_first_byte   = False
            self.is_second_byte  = True
            opcode               = (mosi >> 5) & 0x07
            address              = mosi & 0x1F
            self.current_command = self.OPCODES.get(opcode, f"UNK(0x{opcode:02X})")
            self.last_argument   = address

            if self.current_command == "SR":
                self.bank = 0b00
                return AnalyzerFrame('data', frame.start_time, frame.end_time, {'value': "SOFT RESET"})

            reg = self.REGISTERS.get(self.bank, {}).get(address, f"0x{address:02X}")
            return AnalyzerFrame('data', frame.start_time, frame.end_time, {'value': f"{self.current_command} {reg}"})

        elif self.is_second_byte:
            self.is_second_byte = False

            is_dummy = False
            if self.current_command == "RC":
                a = (self.last_argument >> 4) & 1
                b = (self.last_argument >> 3) & 1
                c = (self.last_argument >> 2) & 1
                d = (self.last_argument >> 1) & 1
                e =  self.last_argument       & 1

                macmii2 = ((~a & ~c) | (~b & d & ~e) | (~b & c & ~e) | (~b & c & d) | (b & ~c & ~d)) & 1
                macmii3 = ((~a & ~b & ~c) | (~a & ~b & c & ~d) | (~a & ~c & d & ~e)) & 1
                is_dummy = (macmii2 and self.bank == 0b10) or (macmii3 and self.bank == 0b11)

            if self.current_command in {"WC", "SB", "CB"} and self.last_argument == 0x1F:
                if self.current_command == "WC":
                    self.bank = mosi & 0b11
                elif self.current_command == "SB":
                    self.bank |= mosi & 0b11
                elif self.current_command == "CB":
                    self.bank &= ~(mosi & 0b11)

            if is_dummy:
                return AnalyzerFrame('data', frame.start_time, frame.end_time, {'value': "DUMMY"})
            else:
                # Only show data value, not bank
                if self.current_command in {"RC", "RB"}:
                    return AnalyzerFrame('data', frame.start_time, frame.end_time, {'value': f"0x{miso:02X}"})
                else:
                    return AnalyzerFrame('data', frame.start_time, frame.end_time, {'value': f"0x{mosi:02X}"})

        else:
            if self.current_command in {"RC", "RB"}:
                return AnalyzerFrame('data', frame.start_time, frame.end_time, {'value': f"0x{miso:02X}"})
            elif self.current_command in {"WC", "WB", "SB", "CB"}:
                return AnalyzerFrame('data', frame.start_time, frame.end_time, {'value': f"0x{mosi:02X}"})

    def decode(self, frame):
        if frame.type == "enable":
            return self.handle_enable(frame)
        elif frame.type == "disable":
            return self.handle_disable(frame)
        elif frame.type == "result":
            return self.handle_result(frame)
        return None

