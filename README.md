bookfinder
==========

bookfinder is a python 2 script that searches a minecraft 1.3.1 world for written books and formats them into text files. Requires the [nbt module](https://github.com/twoolie/nbt).

It currently searches:

* player inventories (`-p`)
* ender chests (`-e`)
* chests (`-c`)
* furnaces (`-f`)
* dispensers (`-t`)
* storage minecarts (`-s`)
* dropped items (aka resources) (`-i`)

Licensed under the GPL2.

installation
------------

If you're an Arch user, download the [PKGBUILD](https://raw.github.com/UncleNinja/bookfinder/master/PKGBUILD) to a directory of your choice and run `makepkg`. If you're looking for `python2-nbt`, you can find it in the [aur](https://aur.archlinux.org/packages.php?ID=59423).

Otherwise:

0. You'll need [python 2](http://python.org). 
1. Make sure you have the python [nbt module](https://github.com/twoolie/nbt). If you don't follow the instructions in that link.
2. Install bookfinder:

    $ git clone git://github.com/UncleNinja/bookfinder.git bookfinder
    $ cd bookfinder
    # install -Dm 755 bookfinder.py $pkgdir/usr/bin/bookfinder

examples
--------

Searching everything in a normal world:

    $ bookfinder -a ~/.minecraft/saves/aworld

Look for books stored in chunks (chests, furnaces, dropped items, etc):

    $ bookfinder -cftsi ~/.minecraft/saves/aworld

Searching data tied to players (ender chests, inventories) :

    $ bookfinder -pe ~/.minecraft/saves/aworld

### searching the nether ###

If you want to search the nether, the just pass in `yourworld/DIM-1` as the world. Don't use the `-p` or `-e` flags because they require searching `/players`, which the nether world folder doesn't have.

For example (searching everything possible with just `/region`):

    $ bookfinder -cftsi ~/.minecraft/saves/aworld/DIM-1

The same except for The End (notice the missing dash):

    $ bookfinder -cftsi ~/.minecraft/saves/aworld/DIM1

help
----

    $ bookfinder --help
    usage: bookfinder [-h] [-d OUTPUT_DIR] [-a] [-c] [-f] [-p] [-i] [-e] [-s] [-t] world
    
    converts books in an anvil world into specially formatted text files
    
    positional arguments:
      world                 path to an anvil world
    
    optional arguments:
      -h, --help            show this help message and exit
      -d OUTPUT_DIR, --output-dir OUTPUT_DIR
                            place to put book text files
      -a, --all             search for books everywhere
      -c, --chests          search chests for books (slow)
      -f, --furnaces        search furnaces for books (slow)
      -p, --inventories     search player inventories for books (very fast)
      -i, --items           search dropped items (sometimes called resources) for
                            books
      -e, --enderchests     search ender chests for books
      -s, --storagecarts    search storage minecarts
      -t, --dispenser       search dispensers (traps)



