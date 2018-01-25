class MFRC522:
    PICC_REQIDL = None
    PICC_AUTHENT1A = None
    MI_OK = None

    def __init__(self, dev='/dev/spidev0.0', spd=1000000):
        pass

    def MFRC522_Reset(self):
        pass

    def Write_MFRC522(self, addr, val):
        pass

    def Read_MFRC522(self, addr):
        return 0

    def SetBitMask(self, reg, mask):
        pass

    def ClearBitMask(self, reg, mask):
        pass

    def AntennaOn(self):
        pass

    def AntennaOff(self):
        pass

    def MFRC522_ToCard(self, command, sendData):
        return self.MI_OK, 0, 0

    def MFRC522_Request(self, reqMode):
        return self.MI_OK, 0

    def MFRC522_Anticoll(self):
        return self.MI_OK, 0

    def CalulateCRC(self, pIndata):
        out_data = []
        return out_data

    def MFRC522_SelectTag(self, serNum):
        back_data = [0]
        return back_data[0]

    def MFRC522_Auth(self, authMode, BlockAddr, Sectorkey, serNum):
        return self.MI_OK

    def MFRC522_StopCrypto1(self):
        pass

    def MFRC522_Read(self, blockAddr):
        pass

    def MFRC522_Write(self, blockAddr, writeData):
        pass

    def MFRC522_DumpClassic1K(self, key, uid):
        pass

    def MFRC522_Init(self):
        pass
