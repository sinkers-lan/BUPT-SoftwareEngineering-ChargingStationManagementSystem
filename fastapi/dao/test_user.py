import dao.user as user_dao
from utils import utils

if __name__ == "__main__":
    psw = utils.hash_password("1234")
    info = user_dao.logon("13911010126", psw, "京AB2431", 45.0)
    if info['code'] == 1:
        pass
