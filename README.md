# epicmods
Check mods for games on Epic Games Shop

This program will allow you to check for updates on mods of games installed with the Epic Games Launcher/Shop.

It uses Steam Games Worshop to check for updates. Unfortunately there aren't any other method yet as long as modders keep to upload them only there.

This program is not able to download the mods, it only helps you check if you need new version and helps installing them.

Beta version. It does save a backup of an old version, as long as it recognize them. You need to store them in a directory named after the ID of the mod.

* Run client.py and add all packages needed. (requests, beautifulsoup and lxml)
* Add the download path. This is where you will put the archives of the mods you downloaded
* Add a mod by using either the ID ( -a ) or the whole url ( -u )
* You might be asked where the mod should be installed if it's your first mod for that game.
* Once you've downloaded the zips, put them in the directory you picked before (must contain only those zips)
* restart the application with -i
* you will then have to clean the mods directory from the old mods, if you had one, since from now on,they will use their ID as directory name