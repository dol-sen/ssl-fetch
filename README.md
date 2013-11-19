SSL-Fetch

This is a convienience lib to reduce code duplication in several
gentoo utility applications.  It can also be useful for other applications
that require ssl connections for downloading files.  It can verify the ssl
connection checking against the known certificates.  It includes the use of
headers for User-Agent, If-Modified-Since, and the loading of a timestamp file.

There is some additional coding still to do.  But it does contain the one
class so far.

I welcome others to suggest additional functionality that they require.

This lib is also python-2.6 and higher compatible using the python
requests package which contains urllib3, and openssl.  There are some
additional dependencies for python versions less than 3.2.

For more project information contact:

Brian Dolbec <dolsen at gentoo dot org>
