#!/usr/bin/python3
# coding=utf-8

#
# This file is a part of HUD mirror script. For more information
# visit official site: https://www.easycoding.org/projects/hudman
#
# Copyright (c) 2016 - 2018 EasyCoding Team.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

from calendar import timegm
from datetime import datetime
from hashlib import md5, sha1
from json import loads
from os import path, makedirs, rename
from shutil import rmtree
from urllib.request import Request, urlopen
from xml.dom import minidom

from .hudlist import HUDEntry
from .hudmsg import HUDMessages, HUDSettings


class HUDMirror:
    @staticmethod
    def gmt2unix(gtime: str) -> int:
        """
        Convert datetime string to unixtime.
        :param gtime: Datetime string.
        :return: UnixTime integer.
        """
        do = datetime.strptime(gtime, '%Y-%m-%dT%H:%M:%SZ')
        return int(timegm(do.timetuple()))

    @staticmethod
    def callgithubapi(repourl: str) -> list:
        """
        Call GitHub API and fetch useful information about project.
        :param repourl: GitHub repository URL.
        :return: List with SHA1 hash and datetime of latest commit.
        """
        url = repourl.replace('https://github.com/', 'https://api.github.com/repos/') + '/commits?per_page=1'
        response = urlopen(Request(url, data=None, headers={'User-Agent': HUDSettings.ua_curl}))
        if response.status != 200:
            raise Exception(HUDMessages.gh_errcode.format(response.status))
        data = loads(response.read().decode('utf-8'))
        return [data[0]['sha'], HUDMirror.gmt2unix(data[0]['commit']['committer']['date'])]

    @staticmethod
    def downloadfile(url: str, name: str, outdir: str) -> str:
        """
        Download file from Internet and save it to specified directory.
        :param url: URL of remote file.
        :param name: Name of result file.
        :param outdir: Output directory.
        :return: Full local path of downloaded file.
        """
        fdir = path.join(outdir, name)
        if not path.exists(fdir):
            makedirs(fdir)
        filepath = path.join(fdir, '{}.zip'.format(name))
        request = Request(url, data=None, headers={'User-Agent': HUDSettings.ua_wget})
        with urlopen(request) as response, open(filepath, 'wb') as result:
            result.write(response.read())
        return filepath

    @staticmethod
    def renamefile(fname: str, chash: str) -> str:
        """
        Rename file using it's hash.
        :param fname: Source file name.
        :param chash: Source file hash sum.
        :return: Full local path of renamed file.
        """
        fdir = path.dirname(fname)
        result = path.join(fdir, '{}_{}.zip'.format(path.splitext(path.basename(fname))[0], chash[:8]))
        rename(fname, result)
        return result

    @staticmethod
    def md5hash(fname: str) -> str:
        """
        Calculate MD5 hash sum of specified file.
        :param fname: Source file name.
        :return: MD5 hash of source file.
        """
        return md5(open(fname, 'rb').read()).hexdigest()

    @staticmethod
    def sha1hash(fname: str) -> str:
        """
        Calculate SHA1 hash sum of specified file.
        :param fname: Source file name.
        :return: SHA1 hash of source file.
        """
        return sha1(open(fname, 'rb').read()).hexdigest()

    @staticmethod
    def logmessage(msg: str) -> None:
        """
        Print message to log.
        :param msg: Message to print.
        """
        print(msg)

    def __checkdb(self) -> bool:
        """
        Check if specified HUD database file exists.
        :return: Return True if HUD database file exists.
        """
        return path.isfile(self.__gamedb)

    def __readdb(self) -> None:
        """
        Read and parse HUD XML database file.
        """
        if not self.__checkdb():
            raise FileNotFoundError(HUDMessages.db_notfound.format(self.__gamedb))

        huddb = minidom.parse(self.__gamedb)
        for hud in huddb.getElementsByTagName('HUD'):
            self.__hudlist.append(HUDEntry(hud.getElementsByTagName("InstallDir")[0].firstChild.data,
                                           hud.getElementsByTagName("UpURI")[0].firstChild.data,
                                           hud.getElementsByTagName("RepoPath")[0].firstChild.data,
                                           hud.getElementsByTagName("LastUpdate")[0].firstChild.data,
                                           hud.getElementsByTagName("URI")[0].firstChild.data))

    def __usegh(self, hud: HUDEntry) -> None:
        """
        Call GitHub and download latest revision of specified HUD.
        :param hud: HUD entry to process and download.
        """
        r = self.callgithubapi(hud.repopath)
        if r[1] > hud.lastupdate:
            f = self.renamefile(self.downloadfile(hud.upstreamuri, hud.hudname, self.__outdir), r[0])
            self.logmessage(HUDMessages.hud_updated_gh.format(hud.hudname, self.md5hash(f), r[1], path.basename(f)))
        else:
            self.logmessage(HUDMessages.hud_uptodate.format(hud.hudname))

    def __useother(self, hud: HUDEntry) -> None:
        """
        Download specified HUD from unknown location.
        :param hud: HUD entry to process and download.
        """
        filednl = self.downloadfile(hud.upstreamuri, hud.hudname, self.__outdir)
        fullfile = self.renamefile(filednl, self.sha1hash(filednl))
        shortfile = path.basename(fullfile)
        if shortfile != hud.filename:
            self.logmessage(HUDMessages.hud_updated_oth.format(hud.hudname, self.md5hash(fullfile), shortfile))
        else:
            rmtree(path.dirname(fullfile))
            self.logmessage(HUDMessages.hud_uptodate.format(hud.hudname))

    def __handlehud(self, hud: HUDEntry) -> None:
        """
        Process and download specified HUD using different backends.
        :param hud: HUD entry to process and download.
        """
        if hud.ghhosted:
            self.__usegh(hud)
        else:
            self.__useother(hud)

    def getall(self) -> None:
        """
        Process and download updates for all HUDs from database.
        """
        for hud in self.__hudlist:
            try:
                self.__handlehud(hud)
            except Exception as ex:
                self.logmessage(HUDMessages.hud_error.format(hud.hudname, ex))

    def __init__(self, gamedb: str, outdir: str) -> None:
        """
        Main constructor of HUDMirror class.
        :param gamedb: Full path to game database file.
        :param outdir: Full path to output directory.
        """
        self.__gamedb = gamedb
        self.__outdir = outdir
        self.__hudlist = []
        self.__readdb()
