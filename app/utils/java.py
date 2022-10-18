import jpype
from app.core.config import conf

config = conf()
classpath = config.BASE_DIR + '/app/modules/kt_crypto-1.0.jar'
print(classpath)
if not jpype.isJVMStarted():
    jpype.startJVM(
        jpype.getDefaultJVMPath(),
        "-Djava.class.path={classpath}".format(classpath=classpath),
        convertStrings=True,
    )

def decode_value(input, key="euc-kr"):
    jpkg = jpype.JPackage('crypto')
    crypto = jpkg.Crypto()
    return crypto.decript(input, key)
