from api.router import Router

if __name__ == '__main__':
    rt = Router()
    rt.listen("127.0.0.1", 6001)
    rt.run()
