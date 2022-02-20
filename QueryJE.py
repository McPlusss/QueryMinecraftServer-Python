import socket


class Server(object):
    """
    用于查询服务器信息
    """
    def __init__(self, Address: str, Port: int):
        """
        构造函数

        :param Address: 服务器地址
        :param Port: 服务器端口
        """
        self.Address = Address
        self.Port = Port
        self.__Socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__AddressTuple = (self.Address, self.Port)
        self.__Socket.bind(("", 1234))

    def BasicQuery(self) -> dict:
        """
        查询基础服务器信息

        :return: 服务器信息字典
        """
        TokenArray = self.__GetTokenArray()
        BasePacketArray = [0xFE, 0xFD, 0x00, 0x00, 0x00, 0x00, 0x01]
        BasePacketBytes = bytes(BasePacketArray)
        BasePacketBytes += self.__PackToken(TokenArray)

        self.__Socket.sendto(BasePacketBytes, self.__AddressTuple)
        return self.__HandleReceive()

    def FullQuery(self) -> dict:
        """
        查询完整服务器信息

        :return: 服务器信息字典
        """
        TokenArray = self.__GetTokenArray()
        BasePacketArray = [0xFE, 0xFD, 0x00, 0x00, 0x00, 0x00, 0x01]
        BasePacketBytes = bytes(BasePacketArray)
        BasePacketBytes += self.__PackToken(TokenArray) + bytes([0x00, 0x00, 0x00, 0x00])

        self.__Socket.sendto(BasePacketBytes, self.__AddressTuple)
        return self.__HandleReceive()

    def __HandleReceive(self) -> dict:
        try:
            self.__Socket.settimeout(15)
            ReceiveData = self.__Socket.recvfrom(4096)
            ResponseData = ReceiveData[0]
            if ResponseData[0] == 0x09:
                print("Token Receive")
                TokenArray = []
                for i in range(5, len(ResponseData) - 1):
                    TokenArray.append(ResponseData[i])
                return {
                    "type": "Token",
                    "data": TokenArray
                }
            elif ResponseData[0] == 0x00 and ResponseData[5] != 0x73:
                print("Basic Stat Receive")
                MessageArray = []
                ArrayTemp = []
                for i in range(5, len(ResponseData)):
                    if ResponseData[i] == 0:
                        MessageArray.append(ArrayTemp)
                        ArrayTemp = []
                    else:
                        ArrayTemp.append(ResponseData[i])
                for i in range(0, len(MessageArray) - 1):
                    MessageArray[i] = bytes(MessageArray[i]).decode()

                StatDict = {
                    "type": "BasicQuery",
                    "data": {
                        "motd": MessageArray[0],
                        "gameType": MessageArray[1],
                        "map": MessageArray[2],
                        "onlinePlayer": MessageArray[3],
                        "maxPlayer": MessageArray[4]
                    }
                }
                return StatDict
            elif ResponseData[0] == 0x00 and ResponseData[5] == 0x73:
                print("Full Stat Receive")
                MessageArray = []
                ArrayTemp = []
                BeforeIsKey = True
                for i in range(16, len(ResponseData)):
                    if ResponseData[i] == 0:
                        if BeforeIsKey:
                            ArrayTemp = []
                            BeforeIsKey = False
                        else:
                            MessageArray.append(ArrayTemp)
                            ArrayTemp = []
                            BeforeIsKey = True
                    else:
                        ArrayTemp.append(ResponseData[i])

                for i in range(0, len(MessageArray)):
                    MessageArray[i] = bytes(MessageArray[i]).decode()

                StatDict = {
                    "type": "FullQuery",
                    "data": {
                        "motd": MessageArray[0],
                        "gameType": MessageArray[1],
                        "gameId": MessageArray[2],
                        "version": MessageArray[3],
                        "plugins": MessageArray[4],
                        "map": MessageArray[5],
                        "onlinePlayer": MessageArray[6],
                        "maxPlayer": MessageArray[7],
                        "host": MessageArray[9] + ":" + MessageArray[8]
                    }
                }
                return StatDict
        except socket.timeout:
            return {
                "type": "Error",
                "data": "Timeout"
            }

    def __GetTokenArray(self) -> list:
        self.__Handshake()

        return self.__HandleReceive()["data"]

    def __Handshake(self):
        PacketArray = [0xFE, 0xFD, 0x09, 0x00, 0x00, 0x00, 0x01]  # 0x00, 0x00, 0x00, 0x01可以更改
        PacketBytes = bytes(PacketArray)
        self.__Socket.sendto(PacketBytes, self.__AddressTuple)

    @staticmethod
    def __PackToken(Token: list) -> bytes:
        return int(bytes(Token)).to_bytes(4, 'big')
