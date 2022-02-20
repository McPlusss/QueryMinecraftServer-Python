from QueryJE import Server

NewServer = Server("localhost", 25566)
BasicQueryDict = NewServer.BasicQuery()
FullQueryDict = NewServer.FullQuery()

print(BasicQueryDict)
print(FullQueryDict)
