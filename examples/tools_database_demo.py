import bioimageit_core.api as iit

# First we connect to the database (here it is a local database)
req = iit.Request('./config_sample.json')

print('- Get the list of all available tools')
req.search_tool()

print('- Get a specific tool from it name and version')
tool = req.get_tool('spitfiredeconv2d_v0.1.2')
if tool:
    print('    Tool found')
    print('- Print the spitfiredeconv2d_v0.1.2 man page:')
    tool.man()
