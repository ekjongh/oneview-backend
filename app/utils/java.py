import jpype
classpath = 'modules/kt_crypto-1.0.jar'
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
