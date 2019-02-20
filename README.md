# android-sms-hash-generator
Small and effective python script to compute the android app's hash to properly configure the SMS Signup with autoverification code.

# Download
Download the latest version from [Releases](https://github.com/funambol/android-sms-hash-generator/releases) page.

# Requirements
- JDK
- Python3

# Usage
smshash.py needs four parameters:
- keystore: the absolute or relative path of your Android keystore
- alias: the alias of the keystore
- keypass: the passphrase of the keystore
- appid: your app's package name
Example:
```python
python3 smshash.py path/keystore MyAndroidKey xxxxxxxxxxxx com.company.name
```

For help:
```python
python3 smshash.py -h
```

>**Please note:**<br>
>On Windows, smshash.py and xxd_w.exe must be placed in the same folder.
><br>xxd_w.exe is not used on other platforms.

# Why
Google Play services uses the hash string to determine which verification messages to send to your Android app. The hash string is made of your app's package name and your app's public key certificate.
According to Google [documentation](https://developers.google.com/identity/sms-retriever/verify#computing_your_apps_hash_string) it can be generated with this command:
```bash
keytool -exportcert -alias MyAndroidKey -keystore MyProductionKeys.keystore | xxd -p | tr -d "[:space:]" | echo -n com.example.myapp `cat` | sha256sum | tr -d "[:space:]-" | xxd -r -p | base64 | cut -c1-11
```
But that command has some issues:
- It's not multi platform: it works fine on Linux, it could work on Mac with a small change, it does not work at all on Windows.
- It does not emit an error if the keytool command fails and it generates the hash of the error message instead.

This python script does not have those issues, it is multi platform and if the keytool command fails (for instance because the keystore passphrase is wrong), the script stops and emit an error message.