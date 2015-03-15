# CACConsole
A Python based console for managing Cloud at Cost servers via the CaC API.

#### Usage

Run `python cacconsole.py`

Type "help" for list of commands (see below). CACConsole can help with managing multiple accounts, add accounts with the following command: `add_account <email> <apikey>`. Then use the `use` command to switch between multiple accounts, example: `use foo@example.com`.

```
   _____ _                 _         _      _____          _   
  / ____| |               | |       | |    / ____|        | |  
 | |    | | ___  _   _  __| |   __ _| |_  | |     ___  ___| |_ 
 | |    | |/ _ \| | | |/ _` |  / _` | __| | |    / _ \/ __| __|
 | |____| | (_) | |_| | (_| | | (_| | |_  | |___| (_) \__ \ |_ 
  \_____|_|\___/ \__,_|\__,_|  \__,_|\__|  \_____\___/|___/\__|
   _____    ____    _   _    _____    ____    _        ______  
  / ____|  / __ \  | \ | |  / ____|  / __ \  | |      |  ____| 
 | |      | |  | | |  \| | | (___   | |  | | | |      | |__    
 | |      | |  | | | . ` |  \___ \  | |  | | | |      |  __|   
 | |____  | |__| | | |\  |  ____) | | |__| | | |____  | |____  
  \_____|  \____/  |_| \_| |_____/   \____/  |______| |______| 
                                                               
                                                               
CloudAtCostConsole Copytright (c) 2015 foospidy
Don't forget to whitelist your IP address in your CaC panel settings.

For help type 'help'.
CaC>help
Valid commands:
	add_account
	banner
	del_account
	help
	list
	ping
	poweroff
	poweron
	quit
	reset
	usage
	use
	whoami
Type "help [command]" for more info.
CaC>
```

#### Dependencies

##### python-cloudatcost
Python library for CaC API (https://github.com/adc4392/python-cloudatcost)

This library is alredy included in CACConsole's modules directory.


##### Twisted
Learn more about Twisted here https://twistedmatrix.com.

To Install on Debian:

`apt-get install python-twisted`
