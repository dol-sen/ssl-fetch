SSL-Fetch

A convenience python library for verified ssl connection downloads.
It uses headers such as User-Agent and If-Modified-Since and the loading of a
timestamp file.  This is a convienience lib to reduce code duplication in
several gentoo utility applications.  It can also be useful for other
applications that require ssl connections for downloading files if they have
been updated since last downloaded.  Returning also the new timestamp you can
save to be ready for the next update check & download.

There is some additional coding still to do.  But it does contain the one
class so far.  We are looking at adding some multiple possibilies to
parrallelize multiple file downloads for one or multiple servers.

I welcome others to suggest additional functionality that they require.

This lib is also python-2.6 and higher compatible using the python
requests package which contains urllib3, and openssl.  There are some
additional dependencies for python versions less than 3.2.  To be updated and
listed later.

For more project information contact:

Brian Dolbec <dolsen at gentoo dot org>

