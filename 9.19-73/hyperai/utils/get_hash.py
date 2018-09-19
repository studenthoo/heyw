from hashlib import sha1


def get_hash(pwd, salt=None):
    pwd = "^*)" + pwd + "#^%"
    sh = sha1()
    sh.update(pwd)
    return sh.hexdigest()
