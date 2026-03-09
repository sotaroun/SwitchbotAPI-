# SwitchBot API Test

PythonでSwitchBot APIを操作するテストプロジェクト

DeviceIDCheck.pyを再生すると、接続しているデバイスIDが一覧で表示される

そのデバイスidと公式マニュアルの操作コマンド(https://github.com/OpenWonderLabs/SwitchBotAPI/blob/main/README.md)
を組み合わせることで、デバイスの操作命令APIを飛ばし、アンドロイドタブレットなどから操作を行える

ここから操作を行う際は、必ずserver.pyのローカルサーバーを立ち上げておく必要がある
server.pyは、スタートメニューまたはタスクバーに固定してあるショートカットからでも起動可能
