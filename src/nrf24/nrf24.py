import pigpio
from enum import Enum, IntEnum
from os import environ as env


class RF24_PA(IntEnum):
    MIN = 0,
    LOW = 1,
    HIGH = 2,
    MAX = 3,
    ERROR = 4

    @staticmethod
    def from_value(value):
        if value is None:
            raise ValueError(f'"None" is not a RF24_PA value.')

        if isinstance(value, RF24_PA):
            return value

        elif isinstance(value, int):
            for e in RF24_PA:
                if value == e.value:
                    return e
            raise ValueError(f'Value {value} is not a RF24_PA value.')

        elif isinstance(value, str):
            for e in RF24_PA:
                if value.lower() == e.name.lower():
                    return e
            raise ValueError(f'Value {value} is not a RF24_PA name.')

        else:
            raise ValueError(f'{value} ({type(value)}) is not a RF24_PA value.')


class RF24_DATA_RATE(IntEnum):
    RATE_1MBPS = 0,
    RATE_2MBPS = 1,
    RATE_250KBPS = 2

    @staticmethod
    def from_value(value):
        if value is None:
            raise ValueError(f'"None" is not a RF24_DATA_RATE value.')

        if isinstance(value, RF24_DATA_RATE):
            return value

        elif isinstance(value, int):
            for e in RF24_DATA_RATE:
                if value == e.value:
                    return e
            raise ValueError(f'Value {value} is not a RF24_DATA_RATE value.')

        elif isinstance(value, str):
            for e in RF24_DATA_RATE:
                if value.lower() == e.name.lower():
                    return e
            raise ValueError(f'Value {value} is not a RF24_DATA_RATE name.')

        else:
            raise ValueError(f'{value} ({type(value)}) is not a RF24_DATA_RATE value.')


class RF24_CRC(IntEnum):
    DISABLED = 0,
    BYTES_1 = 1,
    BYTES_2 = 2

    @staticmethod
    def from_value(value):
        if value is None:
            raise ValueError(f'"None" is not a RF24_CRC value.')

        if isinstance(value, RF24_CRC):
            return value
        elif isinstance(value, int):
            for e in RF24_CRC:
                if value == e.value:
                    return e
            raise ValueError(f'Value {value} is not a RF24_CRC value.')
        elif isinstance(value, str):
            for e in RF24_CRC:
                if value.lower() == e.name.lower():
                    return e
            raise ValueError(f'Value {value} is not a RF24_CRC name.')
        else:
            raise ValueError(f'{value} ({type(value)}) is not an RF24_CRC value.')


class RF24_PAYLOAD(IntEnum):
    ACK = -1
    DYNAMIC = 0
    MIN = 1
    MAX = 32

    @staticmethod
    def from_value(value):
        if value is None:
            raise ValueError(f'"None" is not a RF24_PAYLOAD value.')

        if isinstance(value, RF24_PAYLOAD):
            return value

        elif isinstance(value, int):
            for e in RF24_PAYLOAD:
                if value == e.value:
                    return e
            if value >= ACK and value <= MAX:
                return value

            raise ValueError(f'Value {value} is not a RF24_PAYLOAD value.')

        elif isinstance(value, str):
            for e in RF24_PAYLOAD:
                if value.lower() == e.name.lower():
                    return e                    
            raise ValueError(f'Value {value} is not a RF24_PAYLOAD name.')

        else:
            raise ValueError(f'{value} ({type(value)}) is not an RF24_PAYLOAD value.')


class SPI_CHANNEL(IntEnum):
    MAIN_CE0 = 0
    MAIN_CE1 = 1
    AUX_CE0 = 2
    AUX_CE1 = 3
    AUX_CE2 = 4

    @staticmethod
    def from_value(value):
        if value is None:
            raise ValueError(f'"None" is not a SPI_CHANNEL value.')

        if isinstance(value, SPI_CHANNEL):
            return value

        elif isinstance(value, int):
            for e in SPI_CHANNEL:
                if value == e.value:
                    return e
            
            raise ValueError(f'Value {value} is not a SPI_CHANNEL value.')

        elif isinstance(value, str):
            for e in RF24_PAYLOAD:
                if value.lower() == e.name.lower():
                    return e                    
            raise ValueError(f'Value {value} is not a SPI_CHANNEL name.')

        else:
            raise ValueError(f'{value} ({type(value)}) is not an SPI_CHANNEL value.')
    


class RF24_RX_ADDR(IntEnum):
    P0 = 0x0a,
    P1 = 0x0b,
    P2 = 0x0c,
    P3 = 0x0d,
    P4 = 0x0e,
    P5 = 0x0f


class NRF24:
    """
    Note that RX and TX addresses must match

    Note that communication channels must match:

    Note that payload size must match:

    The following table describes how to configure the operational
    modes.

    +----------+--------+---------+--------+-----------------------------+
    |Mode      | PWR_UP | PRIM_RX | CE pin | FIFO state                  |
    +----------+--------+---------+--------+-----------------------------+
    |RX mode   |  1     |  1      |  1     | ---                         |
    +----------+--------+---------+--------+-----------------------------+
    |TX mode   |  1     |  0      |  1     | Data in TX FIFOs. Will empty|
    |          |        |         |        | all levels in TX FIFOs      |
    +----------+--------+---------+--------+-----------------------------+
    |TX mode   |  1     |  0      |  >10us | Data in TX FIFOs. Will empty|
    |          |        |         |  pulse | one level in TX FIFOs       |
    +----------+--------+---------+--------+-----------------------------+
    |Standby-II|  1     |  0      |  1     | TX FIFO empty               |
    +----------+--------+---------+--------+-----------------------------+
    |Standby-I |  1     |  ---    |  0     | No ongoing transmission     |
    +----------+--------+---------+--------+-----------------------------+
    |Power Down|  0     |  ---    |  ---   | ---                         |
    +----------+--------+---------+--------+-----------------------------+
    """
    
    TX = 0
    RX = 1

    @staticmethod
    def from_config(config, pi=None, pigpio_section='pigpio', nrf24_section='nrf24'):
        

        # Get pigpio configuration.
        if pi is None:
            host = config[pigpio_section].get('host', env.get('PIGPIO_HOST', 'localhost'))
            port = config[pigpio_section].getint('port', env.get('PIGPIO_PORT', 8888))
            pi = pigpio.pi(host, port)
    
        # Get nrf24 configuration
        ce_pin = config[nrf24_section].getint('ce_pin', 25)
        spi_channel = SPI_CHANNEL.from_value(config[nrf24_section].get('spi_channel', SPI_CHANNEL.MAIN_CE0))
        spi_speed = config[nrf24_section].getint('spi_speed', 50e4)
        data_rate = RF24_DATA_RATE.from_value(config['nrf24'].get('data_rate', RF24_DATA_RATE.RATE_1MBPS))
        channel = config[nrf24_section].getint('channel', 76)
        payload_size = RF24_PAYLOAD.from_value(config[nrf24_section].get('payload_size', RF24_PAYLOAD.MAX))
        address_bytes = config[nrf24_section].getint('address_size', 5)
        crc_bytes = RF24_CRC.from_value(config[nrf24_section].getint('address_size', RF24_CRC.BYTES_2))
        pad = config[nrf24_section].getint('pad', 32)

        nrf = NRF24(pi, ce=ce_pin, spi_channel=spi_channel, spi_speed=spi_speed,data_rate=data_rate,channel=channel,payload_size=payload_size,address_bytes=address_bytes,crc_bytes=crc_bytes,pad=pad)

        if config[nrf24_section].get('tx_addr', None) is not None:
            nrf.open_writing_pipe(config[nrf24_section].get('tx_addr', None))
        
        if config[nrf24_section].get('rx_addr_0', None) is not None:
            nrf.open_reading_pipe(0, config[nrf24_section].get('rx_addr_0', None))
        if config[nrf24_section].get(nrf24_section, None) is not None:
            nrf.open_reading_pipe(1, config[nrf24_section].get('rx_addr_1', None))
        if config[nrf24_section].get('rx_addr_2', None) is not None:
            nrf.open_reading_pipe(2, config[nrf24_section].get('rx_addr_2', None))
        if config[nrf24_section].get('rx_addr_3', None) is not None:
            nrf.open_reading_pipe(3, config[nrf24_section].get('rx_addr_3', None))
        if config[nrf24_section].get('rx_addr_4', None) is not None:
            nrf.open_reading_pipe(4, config[nrf24_section].get('rx_addr_4', None))
        if config[nrf24_section].get('rx_addr_5', None) is not None:
            nrf.open_reading_pipe(5, config[nrf24_section].get('rx_addr_5', None))

        return nrf, pi


    def __init__(self,
                 pi,                                    # pigpio Raspberry PI connection
                 ce,                                    # GPIO for chip enable
                 
                 spi_channel=SPI_CHANNEL.MAIN_CE0,      # SPI channel
                 spi_speed=50e3,                        # SPI bps 50.000 = 50 Mhz

                 data_rate=RF24_DATA_RATE.RATE_1MBPS,   # Default data rate is 1 Mbits.
                 channel=76,                            # Radio channel
                 payload_size=RF24_PAYLOAD.MAX,         # Message size in bytes (default: 32)
                 address_bytes=5,                       # RX/TX address length in bytes
                 crc_bytes=RF24_CRC.BYTES_2,            # Number of CRC bytes
                 pad=32                                 # Value used to pad short messages
                 ):

        """
        Instantiate with the Pi to which the card reader is connected.

        Optionally the SPI channel may be specified.  The default is
        main SPI channel 0.

        The following constants may be used to define the channel:

           SPI_MAIN_CE0 - main SPI channel 0
           SPI_MAIN_CE1 - main SPI channel 1
           SPI_AUX_CE0  - aux  SPI channel 0
           SPI_AUX_CE1  - aux  SPI channel 1
           SPI_AUX_CE2  - aux  SPI channel 2
        """

        self._pi = pi

        # Chip Enable can be any PIN (~).
        assert 0 <= ce <= 31
        self._ce_pin = ce
        pi.set_mode(ce, pigpio.OUTPUT)
        self.unset_ce()

        # SPI Channel
        assert spi_channel >= SPI_CHANNEL.MAIN_CE0 and spi_channel <= SPI_CHANNEL.AUX_CE2

        # SPI speed between 32 KHz and 10 MHz
        assert 32000 <= spi_speed <= 10e6

        # Access SPI on the Raspberry PI.
        if spi_channel < SPI_CHANNEL.AUX_CE0: # WAS: NRF24.SPI_AUX_CE0:
            # Main SPI
            self._spi_handle = pi.spi_open(spi_channel, int(spi_speed))
        else:
            # Aux SPI.
            self._spi_handle = pi.spi_open(spi_channel - SPI_CHANNEL.AUX_CE0, int(spi_speed), NRF24._AUX_SPI)

        # NRF data rate
        self._data_rate = data_rate
        self.set_data_rate(data_rate)

        # NRF channel (0-125)
        self._channel = 0
        self.set_channel(channel)

        # NRF Payload size. -1 = Acknowledgement payload, 0 = Dynamic payload size, 1 - 32 = Payload size in bytes.
        self._payload_size = 0
        self.set_payload_size(payload_size)

        # NRF Address width in bytes. Shorter addresses will be padded using the padding above.
        self._address_width = 5
        self.set_address_bytes(address_bytes)

        # NRF CRC bytes. Range 0 - 2.
        self._crc_bytes = 1
        self.set_crc_bytes(crc_bytes)

        # Padding for messages and addresses.
        self._padding = ord(' ')
        self.set_padding(pad)

        # NRF Power Tx
        self._power_tx = 0

        # Initialize NRF.
        self.power_down()
        self._nrf_write_reg(self.SETUP_RETR, 0b11111)
        self.flush_rx()
        self.flush_tx()
        self.power_up_rx()

    def set_channel(self, channel):
        assert 0 <= channel <= 125
        self._channel = channel  # frequency (2400 + channel) MHz
        self._nrf_write_reg(self.RF_CH, self._channel)

    def set_payload_size(self, payload):
        assert RF24_PAYLOAD.ACK <= payload <= RF24_PAYLOAD.MAX
        self._payload_size = payload  # 0 is dynamic payload
        self._configure_payload()

    def set_padding(self, pad):
        try:
            self._padding = ord(pad)
        except:
            self._padding = pad
        assert 0 <= self._padding <= 255

    def set_address_bytes(self, address_bytes):
        assert 3 <= address_bytes <= 5
        self._address_width = address_bytes
        self._nrf_write_reg(self.SETUP_AW, self._address_width - 2)

    def set_crc_bytes(self, crc_bytes):
        assert 1 <= crc_bytes <= 2
        if crc_bytes == 1:
            self._crc_bytes = 0
        else:
            self._crc_bytes = self.CRCO

    def set_data_rate(self, rate):
        # RF24_1MBPS   = 0
        # RF24_2MBPS   = 1
        # RF24_250KBPS = 2
        assert RF24_DATA_RATE.RATE_1MBPS <= rate <= RF24_DATA_RATE.RATE_250KBPS

        # Read current setup value from register.
        value = self._nrf_read_reg(self.RF_SETUP, 1)[0]

        # Reset RF_DR_LOW and RF_DR_HIGH to 00 which is 1 Mbps (default)
        value &= ~(NRF24.RF_DR_LOW | NRF24.RF_DR_HIGH)

        # Set the RF_DR_LOW bit if speed is 250 Kbps
        if rate == RF24_DATA_RATE.RATE_250KBPS: # WAS NRF24.RF24_250KBPS:
            value |= NRF24.RF_DR_LOW
        # Set the RF_DR_HIGH bit if speed is 2 Mbps
        elif rate == RF24_DATA_RATE.RATE_2MBPS: # WAS:NRF24.RF24_2MBPS:
            value |= NRF24.RF_DR_HIGH

        # Write value back to setup register.
        self._nrf_write_reg(self.RF_SETUP, value)

    def get_spi_handle(self):
        return self._spi_handle

    def show_registers(self):
        print("Registers:")
        print("----------")
        print(self.format_config())
        print(self.format_en_aa())
        print(self.format_en_rxaddr())
        print(self.format_setup_aw())
        print(self.format_setup_retr())
        print(self.format_rf_ch())
        print(self.format_rf_setup())
        print(self.format_status())
        print(self.format_observe_tx())
        print(self.format_rpd())
        print(self.format_rx_addr_px())
        print(self.format_tx_addr())
        print(self.format_rx_pw_px())
        print(self.format_fifo_status())
        print(self.format_dynpd())
        print(self.format_feature())
        print("----------")

    def _make_fixed_width(self, msg, width, pad):
        if isinstance(msg, str):
            msg = map(ord, msg)

        msg = list(msg)

        if len(msg) >= width:
            return msg[:width]
        else:
            msg.extend([pad] * (width - len(msg)))
            return msg

    def send(self, data):

        # We expect a list of byte values to be sent.  However, popular types
        # such as string, integer, bytes, and bytearray are handled automatically using
        # this conversion code.
        if not isinstance(data, list):

            if isinstance(data, str):
                data = list(map(ord, data))
            elif isinstance(data, int):
                data = list(data.to_bytes(-(-data.bit_length() // 8), 'little'))              
            else:
                data = list(data)
        
        status = self.get_status()
        if status & (self.TX_FULL | self.MAX_RT):
            self.flush_tx()

        if self._payload_size >= RF24_PAYLOAD.MIN:  # fixed payload
            data = self._make_fixed_width(data, self._payload_size, self._padding)

        self._nrf_command([self.W_TX_PAYLOAD] + data)
        self.power_up_tx()

    # Added 2020-05-01, Bjarne Hansen
    def reset_plos(self):
        v = self._nrf_read_reg(NRF24.RF_CH, 1)[0]
        self._nrf_write_reg(NRF24.RF_CH, v)

    # Changed 2020-05-01, Bjarne Hansen
    # WAS:
    # def ack_payload(self, data):
    #     self._nrf_command([self.W_ACK_PAYLOAD] + data)
    def ack_payload(self, pipe, data):
        self._nrf_command([self.W_ACK_PAYLOAD | (pipe & 0x07)] + data)

    def open_writing_pipe(self, address):
        addr = self._make_fixed_width(address, self._address_width, self._padding)
        self.unset_ce()
        self._nrf_write_reg(self.TX_ADDR, addr)
        self._nrf_write_reg(self.RX_ADDR_P0, addr)
        self.set_ce()

    def open_reading_pipe(self, pipe, address):
        # pipe: RX_ADDR_P0, RX_ADDR_P1, RX_ADDR_P2, RX_ADDR_P3, RX_ADDR_P4, RX_ADDR_P5
        # address: max 5 bytes for P0 and P1, max 1 byte for P2, P3, P4, and P5

        # Validate pipe input.
        if not (isinstance(pipe, int) or isinstance(pipe, RF24_RX_ADDR)):
            raise ValueError(f"pipe must be int or RF24_RX_ADDR enum.")
        
        # If a pipe is given as 0..5 add the 0x0a value corresponding to RX_ADDR_P0
        if (pipe >= 0 and pipe <= 5):
            pipe = pipe + NRF24.RX_ADDR_P0

        if (pipe < NRF24.RX_ADDR_P0 or pipe > NRF24.RX_ADDR_P5):
            raise ValueError(f"pipe out of range ({NRF24.RX_ADDR_P0:02x} <= pipe <= and {NRF24.RX_ADDR_P5:02x}).")
        
        # Adjust address.
        addr = self._make_fixed_width(address, self._address_width, self._padding)
        if pipe > 0x0b:
            addr = addr[:1]
        
        # Update address on NRF24L01 module.
        en_rxaddr = self._nrf_read_reg(NRF24.EN_RXADDR, 1)[0]
        enable = 1 << (pipe - NRF24.RX_ADDR_P0)
        self.unset_ce()
        self._nrf_write_reg(pipe, addr)
        self._nrf_write_reg(NRF24.EN_RXADDR, en_rxaddr | enable)        
        self.set_ce()
        
    def set_local_address(self, address):
        addr = self._make_fixed_width(address, self._address_width, self._padding)
        self.unset_ce()
        self._nrf_write_reg(NRF24.RX_ADDR_P1, addr)
        self.set_ce()

    def set_remote_address(self, raddr):
        addr = self._make_fixed_width(raddr, self._address_width, self._padding)
        self.unset_ce()
        self._nrf_write_reg(self.TX_ADDR, addr)
        self._nrf_write_reg(self.RX_ADDR_P0, addr)      # Required for automatic acknowledgements.
        self.set_ce()

    def data_ready_pipe(self):
        status = self.get_status()
        pipe = (status >> 1) & 0x07

        if status & self.RX_DR:
            return True, pipe

        fifo_status = self._nrf_read_reg(self.FIFO_STATUS, 1)[0]
        if fifo_status & self.FRX_EMPTY:
            return False, pipe
        else:            
            return True, pipe

    def data_pipe(self):
        status = self.get_status()
        pipe = (status >> 1) & 0x07
        return pipe

    def data_ready(self):
        
        status = self.get_status()
        if status & self.RX_DR:
            return True

        fifo_status = self._nrf_read_reg(self.FIFO_STATUS, 1)[0]
        if fifo_status & self.FRX_EMPTY:
            return False
        else:            
            return True

    def is_sending(self):
        if self._power_tx > 0:
            status = self.get_status()
            if status & (self.TX_DS | self.MAX_RT):
                self.power_up_rx()
                return False
            return True
        return False

    def get_payload(self):
        if self._payload_size < RF24_PAYLOAD.MIN: 
            # dynamic payload
            bytes_count = self._nrf_command([self.R_RX_PL_WID, 0])[1]
        else:
            # fixed payload   
            bytes_count = self._payload_size

        d = self._nrf_read_reg(self.R_RX_PAYLOAD, bytes_count)
        self.unset_ce()     # added
        self._nrf_write_reg(self.STATUS, self.RX_DR)
        self.set_ce()       # added
        return d

    def get_status(self):
        return self._nrf_command(self.NOP)[0]

    def power_up_tx(self):
        self.unset_ce()
        self._power_tx = 1
        config = self.EN_CRC | self._crc_bytes | self.PWR_UP
        self._nrf_write_reg(self.CONFIG, config)
        self._nrf_write_reg(self.STATUS, self.RX_DR | self.TX_DS | self.MAX_RT)
        self.set_ce()

    def power_up_rx(self):
        self.unset_ce()
        self._power_tx = 0
        config = self.EN_CRC | self._crc_bytes | self.PWR_UP | self.PRIM_RX
        self._nrf_write_reg(self.CONFIG, config)
        self._nrf_write_reg(self.STATUS, self.RX_DR | self.TX_DS | self.MAX_RT)
        self.set_ce()

    def power_down(self):
        self.unset_ce()
        self._nrf_write_reg(self.CONFIG, self.EN_CRC | self._crc_bytes)

    def set_ce(self):
        self._pi.write(self._ce_pin, 1)

    def unset_ce(self):
        self._pi.write(self._ce_pin, 0)

    def flush_rx(self):
        self._nrf_command(self.FLUSH_RX)

    def flush_tx(self):
        self._nrf_command(self.FLUSH_TX)

    def _nrf_xfer(self, data):
        b, d = self._pi.spi_xfer(self._spi_handle, data)
        return d

    def _nrf_command(self, arg):
        if type(arg) is not list:
            arg = [arg]
        return self._nrf_xfer(arg)

    def _nrf_read_reg(self, reg, count):
        return self._nrf_xfer([reg] + [0] * count)[1:]

    def _nrf_write_reg(self, reg, arg):
        """
        Write arg (which may be one or more bytes) to reg.

        This function is only permitted in a powerdown or
        standby mode.
        """
        if type(arg) is not list:
            arg = [arg]
        self._nrf_xfer([self.W_REGISTER | reg] + arg)

    def _configure_payload(self):
        if self._payload_size >= RF24_PAYLOAD.MIN:                      # fixed payload
            self._nrf_write_reg(NRF24.RX_PW_P0, self._payload_size)
            self._nrf_write_reg(NRF24.RX_PW_P1, self._payload_size)
            self._nrf_write_reg(NRF24.DYNPD, 0)
            self._nrf_write_reg(NRF24.FEATURE, 0)
        else:                                                           # dynamic payload
            self._nrf_write_reg(NRF24.RX_PW_P0, 0)
            self._nrf_write_reg(NRF24.RX_PW_P1, 0)
            self._nrf_write_reg(NRF24.DYNPD, NRF24.DPL_P0 | NRF24.DPL_P1 | NRF24.DPL_P2 | NRF24.DPL_P3 | NRF24.DPL_P4 | NRF24.DPL_P5 | NRF24.DPL_P6 | NRF24.DPL_P7)
            if self._payload_size == RF24_PAYLOAD.ACK: 
                self._nrf_write_reg(NRF24.FEATURE, NRF24.EN_DPL | NRF24.EN_ACK_PAY)
            else:
                self._nrf_write_reg(NRF24.FEATURE, NRF24.EN_DPL)

    # Constants related to NRF24 configuration/operation.
    _AUX_SPI = (1 << 8)

    R_REGISTER = 0x00               # reg in bits 0-4, read 1-5 bytes
    W_REGISTER = 0x20               # reg in bits 0-4, write 1-5 bytes

    R_RX_PL_WID = 0x60
    R_RX_PAYLOAD = 0x61             # read 1-32 bytes

    W_TX_PAYLOAD = 0xA0             # write 1-32 bytes
    W_ACK_PAYLOAD = 0xA8            # pipe in bits 0-2, write 1-32 bytes
    W_TX_PAYLOAD_NO_ACK = 0xB0      # no ACK, write 1-32 bytes

    FLUSH_TX = 0xE1
    FLUSH_RX = 0xE2
    REUSE_TX_PL = 0xE3

    NOP = 0xFF                      # no operation

    CONFIG = 0x00
    EN_AA = 0x01
    EN_RXADDR = 0x02
    SETUP_AW = 0x03
    SETUP_RETR = 0x04
    RF_CH = 0x05
    RF_SETUP = 0x06
    STATUS = 0x07
    OBSERVE_TX = 0x08
    RPD = 0x09
    RX_ADDR_P0 = 0x0A
    RX_ADDR_P1 = 0x0B
    RX_ADDR_P2 = 0x0C
    RX_ADDR_P3 = 0x0D
    RX_ADDR_P4 = 0x0E
    RX_ADDR_P5 = 0x0F
    TX_ADDR = 0x10
    RX_PW_P0 = 0x11
    RX_PW_P1 = 0x12
    RX_PW_P2 = 0x13
    RX_PW_P3 = 0x14
    RX_PW_P4 = 0x15
    RX_PW_P5 = 0x16
    FIFO_STATUS = 0x17
    DYNPD = 0x1C
    FEATURE = 0x1D

    # CONFIG
    MASK_RX_DR = 1 << 6
    MASK_TX_DS = 1 << 5
    MASK_MAX_RT = 1 << 4

    EN_CRC = 1 << 3                 # 8 (default)
    CRCO = 1 << 2                   # 4
    PWR_UP = 1 << 1                 # 2
    PRIM_RX = 1 << 0                # 1

    def format_config(self):
        v = self._nrf_read_reg(NRF24.CONFIG, 1)[0]
        s = f"CONFIG: (0x{v:02x}) => "

        if v & NRF24.MASK_RX_DR:
            s += "no RX_DR IRQ, "
        else:
            s += "RX_DR IRQ, "

        if v & NRF24.MASK_TX_DS:
            s += "no TX_DS IRQ, "
        else:
            s += "TX_DS IRQ, "

        if v & NRF24.MASK_MAX_RT:
            s += "no MAX_RT IRQ, "
        else:
            s += "MAX_RT IRQ, "

        if v & NRF24.EN_CRC:
            s += "CRC on, "
        else:
            s += "CRC off, "

        if v & NRF24.CRCO:
            s += "CRC 2 byte, "
        else:
            s += "CRC 1 byte, "

        if v & NRF24.PWR_UP:
            s += "Power up, "
        else:
            s += "Power down, "

        if v & NRF24.PRIM_RX:
            s += "RX"
        else:
            s += "TX"

        return s

    # EN_AA
    ENAA_P5 = 1 << 5  # default
    ENAA_P4 = 1 << 4  # default
    ENAA_P3 = 1 << 3  # default
    ENAA_P2 = 1 << 2  # default
    ENAA_P1 = 1 << 1  # default
    ENAA_P0 = 1 << 0  # default

    def format_en_aa(self):
        v = self._nrf_read_reg(NRF24.EN_AA, 1)[0]
        s = f"EN_AA: (0x{v:02x}) => "
        for i in range(6):
            if v & (1 << i):
                s += f"P{i}:ACK "
            else:
                s += f"P{i}:no ACK "
        return s

    # EN_RXADDR
    ERX_P5 = 1 << 5
    ERX_P4 = 1 << 4
    ERX_P3 = 1 << 3
    ERX_P2 = 1 << 2
    ERX_P1 = 1 << 1  # default
    ERX_P0 = 1 << 0  # default

    def format_en_rxaddr(self):
        v = self._nrf_read_reg(NRF24.EN_RXADDR, 1)[0]
        s = f"EN_RXADDR: (0x{v:02x}) => "
        for i in range(6):
            if v & (1 << i):
                s += f"P{i}:on "
            else:
                s += f"P{i}:off "
        return s

    # SETUP_AW (Address width)
    AW_3 = 1
    AW_4 = 2
    AW_5 = 3      # default

    def format_setup_aw(self):
        v = self._nrf_read_reg(NRF24.SETUP_AW, 1)[0]
        s = f"SETUP_AW: (0x{v:02x}) => address width bytes "
        if v == NRF24.AW_3:
            s += "3"
        elif v == NRF24.AW_4:
            s += "4"
        elif v == NRF24.AW_5:
            s += "5"
        else:
            s += "invalid"
        return s

    # SETUP_RETR (Retry delay and retries)
    # ARD 7-4
    # ARC 3-0
    def format_setup_retr(self):
        v = self._nrf_read_reg(NRF24.SETUP_RETR, 1)[0]
        ard = (((v >> 4) & 15) * 250) + 250
        arc = v & 15
        s = f"SETUP_RETR: (0x{v:02x}) => retry delay {ard} us, retries {arc}"
        return s

    # RF_CH (Channel)
    # RF_CH 6-0
    def format_rf_ch(self):
        v = self._nrf_read_reg(NRF24.RF_CH, 1)[0]
        s = f"RF_CH: (0x{v:02x}) => channel={v & 127}"
        return s

    # RF_SETUP
    CONT_WAVE = 1 << 7
    RF_DR_LOW = 1 << 5
    PLL_LOCK = 1 << 4
    RF_DR_HIGH = 1 << 3

    # RF_PWR  2-1
    def format_rf_setup(self):
        v = self._nrf_read_reg(NRF24.RF_SETUP, 1)[0]
        s = f"RF_SETUP: (0x{v:02x}) => "

        if v & NRF24.CONT_WAVE:
            s += "continuos carrier on, "
        else:
            s += "no continuous carrier, "

        if v & NRF24.PLL_LOCK:
            s += "force PLL lock on, "
        else:
            s += "no force PLL lock, "

        dr = 0
        if v & NRF24.RF_DR_LOW:
            dr += 2
        if v & NRF24.RF_DR_HIGH:
            dr += 1

        if dr == 0:
            s += "1 Mbps, "
        elif dr == 1:
            s += "2 Mbps, "
        elif dr == 2:
            s += "250 kbps, "
        else:
            s += "illegal speed, "

        pwr = (v >> 1) & 3
        if pwr == 0:
            s += "-18 dBm"
        elif pwr == 1:
            s += "-12 dBm"
        elif pwr == 2:
            s += "-6 dBm"
        else:
            s += "0 dBm"
        return s

    # STATUS
    RX_DR = 1 << 6
    TX_DS = 1 << 5
    MAX_RT = 1 << 4
    # RX_P_NO 3-1
    RX_P_NO = 1
    TX_FULL = 1 << 0

    def format_status(self):
        v = self._nrf_read_reg(NRF24.STATUS, 1)[0]
        s = f"STATUS: (0x{v:02x}) => "

        if v & NRF24.RX_DR:
            s += "RX data, "
        else:
            s += "no RX data, "

        if v & NRF24.TX_DS:
            s += "TX ok, "
        else:
            s += "no TX, "

        if v & NRF24.MAX_RT:
            s += "TX retries bad, "
        else:
            s += "TX retries ok, "

        p = (v >> 1) & 7
        if p < 6:
            s += f"pipe {p} data, "
        elif p == 6:
            s += "PIPE 6 ERROR, "
        else:
            s += "no pipe data, "

        if v & NRF24.TX_FULL:
            s += "TX FIFO full"
        else:
            s += "TX FIFO not full"

        return s

    # OBSERVE_TX
    # PLOS_CNT 7-4
    # ARC_CNT 3-0
    def format_observe_tx(self):
        v = self._nrf_read_reg(NRF24.OBSERVE_TX, 1)[0]
        plos = (v >> 4) & 15
        arc = v & 15
        s = f"OBSERVE_TX: (0x{v:02x}) => lost packets {plos}, retries {arc}"
        return s

    # RPD
    # RPD 1 << 0
    def format_rpd(self):
        v = self._nrf_read_reg(NRF24.RPD, 1)[0]
        s = f"RPD: (0x{v:02x}) => received power detector {v & 1}"
        return s

    # RX_ADDR_P0 - RX_ADDR_P5
    @staticmethod
    def _byte2hex(s):
        hex_value = ''.join('{:02x}'.format(c) for c in reversed(s))
        return hex_value

    def format_rx_addr_px(self):
        p0 = self._nrf_read_reg(NRF24.RX_ADDR_P0, 5)
        p1 = self._nrf_read_reg(NRF24.RX_ADDR_P1, 5)
        p2 = self._nrf_read_reg(NRF24.RX_ADDR_P2, 1)[0]
        p3 = self._nrf_read_reg(NRF24.RX_ADDR_P3, 1)[0]
        p4 = self._nrf_read_reg(NRF24.RX_ADDR_P4, 1)[0]
        p5 = self._nrf_read_reg(NRF24.RX_ADDR_P5, 1)[0]

        s = "RX ADDR_PX: "
        s += f"P0=0x{self._byte2hex(p0)} "
        s += f"P1=0x{self._byte2hex(p1)} "
        s += f"P2=0x{p2:02x} "
        s += f"P3=0x{p3:02x} "
        s += f"P4=0x{p4:02x} "
        s += f"P5=0x{p5:02x}"

        return s

    # TX_ADDR
    def format_tx_addr(self):
        p0 = self._nrf_read_reg(NRF24.TX_ADDR, 5)
        s = f"TX_ADDR: 0x{self._byte2hex(p0)} "
        return s

    # RX_PW_P0 - RX_PW_P5
    def format_rx_pw_px(self):
        p0 = self._nrf_read_reg(NRF24.RX_PW_P0, 1)[0]
        p1 = self._nrf_read_reg(NRF24.RX_PW_P1, 1)[0]
        p2 = self._nrf_read_reg(NRF24.RX_PW_P2, 1)[0]
        p3 = self._nrf_read_reg(NRF24.RX_PW_P3, 1)[0]
        p4 = self._nrf_read_reg(NRF24.RX_PW_P4, 1)[0]
        p5 = self._nrf_read_reg(NRF24.RX_PW_P5, 1)[0]
        s = "RX_PW_PX: "
        s += f"P0={p0:02x} P1={p1:02x} P2={p2:02x} P3={p3:02x} P4={p4:02x} P5={p5:02x} "
        return s

    # FIFO_STATUS
    FTX_REUSE = 1 << 6
    FTX_FULL = 1 << 5
    FTX_EMPTY = 1 << 4
    FRX_FULL = 1 << 1
    FRX_EMPTY = 1 << 0

    def format_fifo_status(self):
        v = self._nrf_read_reg(NRF24.FIFO_STATUS, 1)[0]
        s = f"FIFO_STATUS: (0x{v:02x}) => "

        if v & NRF24.FTX_REUSE:
            s += "TX reuse set, "
        else:
            s += "TX reuse not set, "

        if v & NRF24.FTX_FULL:
            s += "TX FIFO full, "
        elif v & NRF24.FTX_EMPTY:
            s += "TX FIFO empty, "
        else:
            s += "TX FIFO has data, "

        if v & NRF24.FRX_FULL:
            s += "RX FIFO full, "
        elif v & NRF24.FRX_EMPTY:
            s += "RX FIFO empty"
        else:
            s += "RX FIFO has data"

        return s

    # DYNPD
    DPL_P7 = 1 << 7
    DPL_P6 = 1 << 6
    DPL_P5 = 1 << 5
    DPL_P4 = 1 << 4
    DPL_P3 = 1 << 3
    DPL_P2 = 1 << 2
    DPL_P1 = 1 << 1
    DPL_P0 = 1 << 0

    def format_dynpd(self):
        v = self._nrf_read_reg(NRF24.DYNPD, 1)[0]
        s = f"DYNPD: (0x{v:02x}) => "
        for i in range(6):
            if v & (1 << i):
                s += f"P{i}:on "
            else:
                s += f"P{i}:off "
        return s

    # FEATURE
    EN_DPL = 1 << 2
    EN_ACK_PAY = 1 << 1
    EN_DYN_ACK = 1 << 0

    def format_feature(self):
        v = self._nrf_read_reg(NRF24.FEATURE, 1)[0]
        s = f"FEATURE: (0x{v:02x}) => "

        if v & NRF24.EN_DPL:
            s += "Dynamic payload on, "
        else:
            s += "Dynamic payload off, "

        if v & NRF24.EN_ACK_PAY:
            s += "ACK payload on, "
        else:
            s += "ACK payload off, "

        if v & NRF24.EN_DYN_ACK:
            s += "W_TX_PAYLOAD_NOACK on"
        else:
            s += "W_TX_PAYLOAD_NOACK off"

        return s
