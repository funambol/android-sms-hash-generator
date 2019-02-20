import platform
import os
import sys
import argparse
import subprocess
from subprocess import Popen, PIPE
import base64
from shutil import which
try:
    import hashlib
except ImportError:
    sys.exit("please install 'hashlib' module: pip install hashlib")

#the parser
cmd_parser = argparse.ArgumentParser(description="Computing app's hash string for Android SMS handling")
cmd_parser.add_argument('keystore', type=str, help='Keystore file')
cmd_parser.add_argument('alias', type=str, help='Keystore alias')
cmd_parser.add_argument('keypass', type=str, help='Key password')
cmd_parser.add_argument('appid', type=str, help='Package name of the Android app')
args = cmd_parser.parse_args()

__encoding_name__ = "iso-8859-1" # Latin 1

def isWindows():
    return platform.system() == "Windows"

def cmdExist(program):
    return which(program) is not None

def exitWithError(error):
    print(error, file=sys.stderr)
    sys.exit()

def call(cmd):
    cmd = subprocess.Popen(cmd, shell=True, universal_newlines=True, stdout=PIPE, stderr=PIPE, encoding=__encoding_name__)
    cmdResult = cmd.communicate()
    return (cmd.returncode, cmdResult[0], cmdResult[1])

def getKeytoolCommand(withxxd = False):
    keytoolName = "keytool"
    if not cmdExist(keytoolName):
        exitWithError("Error: keytool command not found. Be sure the JDK is installed and available in the PATH")

    if withxxd:
        return keytoolName + " " + "-alias " + args.alias + " -exportcert -keystore " + args.keystore + " -storepass " + args.keypass + " | " + getxxdName() + " -p"
    else:
        return keytoolName + " " + "-alias " + args.alias + " -exportcert -keystore " + args.keystore + " -storepass " + args.keypass

def getxxdName():
    xxdName = "xxd"
    if isWindows():
        xxdName = "xxd_w"
    if not cmdExist(xxdName):
        exitWithError("Error: " + xxdName + " not found. If you are on Windows, the program xxd_w.exe must be placed in the current folder")
    return xxdName

def getSignature():
    keytoolCommand = getKeytoolCommand()
    returncode, out, err = call(keytoolCommand)
    if returncode != 0:
        print(out)
        print(err)
        exitWithError("keytool command failed. Please check the alias and the password are correct")
    return out

def getHexSignature():
    keytoolWithxxd = getKeytoolCommand(True)
    returncode, out, err = call(keytoolWithxxd)
    if returncode != 0:
        print(out)
        print(err)
        exitWithError("keytool | xxd command failed")
    return out

def removeWhitespaces(value):
    return "".join(value.split())

def appendApplicationId(value):
    return args.appid + " " + value

def computeSha256(value):
    m = hashlib.sha256()
    m.update(value.encode(__encoding_name__))
    return m.digest()

def formatSignature(signature):
    signatureNoSpaces = removeWhitespaces(signature)
    return appendApplicationId(signatureNoSpaces)

# Call getSignature() to check if the alias and password provided are correct: if not correct the program exits with error
signature = getSignature()
hexSignature = getHexSignature()

formattedSignature = formatSignature(hexSignature)
sha256 = computeSha256(formattedSignature)
base64 = base64.b64encode(sha256)

# The hash to use for the SMS is the first 11 chars
print(base64.decode(__encoding_name__)[0:11])