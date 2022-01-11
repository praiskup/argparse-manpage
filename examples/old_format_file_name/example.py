from optparse import OptionParser


# This function returns a OptionParser
def get_parser():
    parser = OptionParser(
        usage="The usage.",
        description="This program does nothing.")
    parser.add_option("-f", "--file", dest="filename",
                      help="write report to FILE", metavar="FILE")
    parser.add_option("-q", "--quiet",
                      action="store_false", dest="verbose", default=True,
                      help="don't print status messages to stdout")
    return parser
