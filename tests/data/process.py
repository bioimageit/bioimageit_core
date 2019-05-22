#!/usr/bin/python

import sys, getopt

def main(argv):
   text = ''
   outputfile = ''
   try:
      opts, args = getopt.getopt(argv,"ht:o:",["text=","ofile="])
   except getopt.GetoptError:
      print('process.py -i <inputfile> -o <outputfile>')
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print('process.py -text <filecontent> -o <outputfile>')
         sys.exit()
      elif opt in ("-t", "--text"):
         text = arg
      elif opt in ("-o", "--ofile"):
         outputfile = arg

   f = open(outputfile, 'w')
   f.write(text)
   f.close()

if __name__ == "__main__":
   main(sys.argv[1:])

