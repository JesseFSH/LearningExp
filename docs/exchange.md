# 概述

升级主要分为mailbox server和cas server，其中mailbox server即DAG members，升级过程中参考了以下官方文档：  
[Anti-Virus Software in the Operating System on Exchange Servers](https://docs.microsoft.com/en-us/exchange/anti-virus-software-in-the-operating-system-on-exchange-servers-exchange-2013-help)  
[Exchange admin center in Exchange 2013](https://docs.microsoft.com/en-us/exchange/exchange-admin-center-in-exchange-2013-exchange-2013-help)  
[Managing database availability groups](https://docs.microsoft.com/en-us/exchange/managing-database-availability-groups-exchange-2013-help)  

本次升级了解到了以下几点实践经验：  

- 建议exchange所有节点之间端口全开
- 建议打开ipv6（经观察节点之间的心跳联系会以ipv6地址进行）
- 升级Cu补丁时，建议`cd`到所在目录以`./<patch_name>`运行，而非直接双击运行
- exchange 2013环境中，只有cas角色才能访问owa和ecp，即`https://<CasServerName>/owa`和`https://<CasServerName>/ecp`  

- 对于exchange server上安装的杀毒软件，需要对exchange安装目录和db所在的目录添加例外。按照官方文档，还需要对exchange进程添加例外，但是进程工作时需要访问的文件已经被添加，所以进程级别没有做了。

下面开始升级步骤。

## mailbox server升级步骤

1. 传输队列状态设置为drain`Set-ServerComponentState <ServerName> -Component HubTransport -State Draining -Requester Maintenance`

2. 传输队列开始drain`Restart-Service MSExchangeTransport`

3. 将server服务切换到dag内其他服务器`Redirect-Message-Server <ServerName1> -Target <ServerName2>`

4. 暂停该节点`Suspend-ClusterNode -Name <ServerName>`

5. 把该台server上的active db迁移到其他server上`Set-MailboxServer <ServerName> -DatabaseCopyActivationDisabledAndMoveNow $True`

6. 避免在该台server上自动active db`Set-MailboxServer <ServerName> -DatabaseCopyAutoActivationPolicy Blocked`

7. 把服务器置为维护模式`Set-ServerComponentState <ServerName> -Component ServerWideOffline -State Inactive -Requester Maintenance`

8. 安装Cu`Setup.exe /m:upgrade /IAcceptExchangeServerLicenseTerms`

附上验证server已处于维护模式命令：  
To verify the server has been placed into maintenance mode, run `Get-ServerComponentState <ServerName> | ft Component,State -Autosize`  
To verify the server is not hosting any active database copies, run `Get-MailboxServer <ServerName> | ft DatabaseCopy* -Autosize`  
To verify that the node is paused, run `Get-ClusterNode <ServerName> | fl`  
To verify that all transport queues have been drained, run `Get-Queue`  

## mailbox server升级后恢复服务步骤

1. ServerWideOffline组件恢复`Set-ServerComponentState <ServerName> -Component ServerWideOffline -State Active -Requester Maintenance`  

2. 集群内恢复 `Resume-ClusterNode <ServerName>`  

3. server上可以active db`Set-MailboxServer <ServerName> -DatabaseCopyActivationDisabledAndMoveNow $False`

4. server上可以active db`Set-MailboxServer <ServerName> -DatabaseCopyAutoActivationPolicy Unrestricted`

5. 传输服务开启`Set-ServerComponentState <ServerName> -Component HubTransport -State Active -Requester Maintenance`

6. 重启传输服务`Restart-Service MSExchangeTransport`

## cas server升级以及服务恢复步骤

再此不赘述，区别在于运行Cu之前在windows nlb内block掉server ip（具体情况视架构而定）
