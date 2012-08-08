#!/usr/bin/env python2
# bookfinder - finds all signed books in a minecraft world and converts them to text files
# Copyright (C) Austin and Gwen Adams 
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the 
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

# requires python nbt modules (github.com/twoolie/NBT)

import re
import os
import sys
from nbt.nbt import NBTFile
from textwrap import TextWrapper
from collections import namedtuple
from nbt.world import AnvilWorldFolder
from argparse import Action, ArgumentParser, ArgumentTypeError

bookid = 387
bookwidth = 24

Arg = namedtuple("Arg", ["dest", "flags", "help"])
searchargs = (
    Arg("chests", ("-c", "--chests"), "search chests for books (slow)"),
    Arg("furnaces", ("-f", "--furnaces"), "search furnaces for books (slow)"),
    Arg("inventories", ("-p", "--inventories"), "search player inventories for books (very fast)"),
    Arg("items", ("-i", "--items"), "search dropped items (sometimes called resources) for books"),
    Arg("enderitems", ("-e", "--enderchests"), "search ender chests for books"),
    Arg("storagecarts", ("-s", "--storagecarts"), "search storage minecarts"),
    Arg("traps", ("-t", "--dispenser"), "search dispensers (traps)"),
)

class Book (object) :
    def __init__ (self, nbttag) :
        self.author = nbttag["author"].value
        self.title = nbttag["title"].value
        self.pages = []
        
        for page in nbttag["pages"] :
            self.pages.append(page.value)
        
def scanitems (itemtag) :
    for item in itemtag :
        if item["id"].value == bookid :
            yield Book(item["tag"])

def scanplayers (pl, inventory=False, enderitems=False) :
    search = []

    if inventory :
        search.append("Inventory")
    if enderitems :
        search.append("EnderItems")

    for i in os.listdir(pl) :
        dat = os.path.join(pl, i)
        n = NBTFile(dat, "rb")

        for s in search :
            for j in n[s] :
                if j["id"].value == bookid :
                    yield Book(j["tag"])

def scanentities (wf, furnaces=False, chests=False, traps=False, items=False, storagecarts=False) : 
    for coords in wf.regionfiles :
        region = wf.get_region(coords[0], coords[1])
        for j in region.get_chunks() :
            c = region.get_chunk(j['x'], j['z'])
            l = c["Level"]

            # search tile entities in this column for books
            if (furnaces or chests or traps) and len(l["TileEntities"]) :
                for k in l["TileEntities"] :    
                    if (k["id"].value == "Chest" and chests) or (k["id"].value == "Furnace" and furnaces) or (k["id"].value == "Trap" and traps):
                        for i in scanitems(k["Items"]) :
                            yield i

            if (items or storagecarts) and len(l["Entities"]) :
                for e in l["Entities"] :
                    #print e["Item"]
                    if items and e["id"].value == "Item" and e["Item"]["id"].value == bookid :
                        yield Book(e["Item"]["tag"])
                    elif storagecarts and e["id"].value == "Minecart" and e["Type"].value == 1 :
                        for i in scanitems(e["Items"]) :
                            yield i
                #print "r.%s.%s.mca | %s,%s" % (coords[0], coords[1], j["x"], j["z"])


def mktitle (word, titlechar) :
    return word + "\n" + (titlechar*len(word)) + "\n\n"

def sanitizefilename (src, default="book") :
    name = src.lower()

    # hopefully these don't need to be compiled because of the regex cache
    for replaceset in ((r"\s+", "-"), (r"[^-_a-z0-9]+", "")) :
        name = re.sub(*replaceset, string=name)

    # remove psuedo-whitespace from the ends of the string
    name = name.strip("-")

    # if the name is empty, just make the name "book"
    return name or default 

def argdir (directory) :
    if not os.path.isdir(directory) :
        raise ArgumentTypeError("%s is not a directory")
    else :
        return directory

class SearchAll (Action) :
    def __call__ (self, parser, namespace, values, option_string=None) :
        for arg in searchargs :
            setattr(namespace, arg.dest, True)

if __name__ == "__main__" :
    parser = ArgumentParser(description="converts books in an anvil world into specially formatted text files")
    parser.add_argument("world", help="path to an anvil world", type=argdir)
    parser.add_argument("-d", "--output-dir", help="place to put book text files", type=argdir, default=".")
    parser.add_argument("-a", "--all", help="search for books everywhere", nargs=0, action=SearchAll)

    # search different dimensions
    #Arg("overworld", ("-o", "--overworld"), "search the overworld"),
    #Arg("nether", ("-n", "--nether"), "search the nether too"),
    #Arg("theend", ("-z", "--theend"), "search the end"),

    # add all the search-related arguments
    for arg in searchargs :
        parser.add_argument(*arg.flags, help=arg.help, dest=arg.dest, action="store_true")

    args = parser.parse_args()

    print args

    books = []

    if args.chests or args.furnaces or args.traps or args.items or args.storagecarts :    
        wf = AnvilWorldFolder(args.world)

        # okay, you have to admit that this one liner is a little bit cool 
        print "scanning %s (this will take a while)..." % ", ".join(filter(lambda x: getattr(args, x), ("chests", "furnaces", "items")))
        books += list(scanentities(wf, args.furnaces, args.chests, args.traps, args.items, args.storagecarts))

    if args.inventories or args.enderitems :
        playerlocation = os.path.join(args.world, "players")

        print "scanning player inventories..."
        books += list(scanplayers(playerlocation, args.inventories, args.enderitems))

    print "%s books found" % len(books)

    if books :
        wrapper = TextWrapper(width=bookwidth, replace_whitespace=False)

        for book in books :
            # create a sane file name
            newtitle = sanitizefilename(book.title)

            basename = os.path.join(args.output_dir, newtitle+".txt")
            name = basename
            attempt = 0

            while os.path.isfile(name) :
                attempt += 1
                name = "%s.%s" % (basename, attempt)

            f = open(name, "w")
            # create book title
            f.write(mktitle("%s by %s" % (book.title, book.author), "="))

            pages = len(book.pages)
            for i, page in enumerate(book.pages) :
                # create page title
                f.write(mktitle("Page %s of %s" % (i+1, pages), "-")) 
                # wrap the contents of each page just like a minecraft book
                f.write(wrapper.fill(page))
                # create spacer in between pages
                f.write("\n\n")

            f.close()
            print "%s written to %s" % (book.title, name)

             

