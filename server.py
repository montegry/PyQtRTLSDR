import rtlsdr

server = rtlsdr.RtlSdrTcpServer(hostname='192.168.1.21', port=111)
server.run_forever()
