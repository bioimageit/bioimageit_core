import sys, getopt

def main(argv):

    # parse args
    message = ''
    ofile = ''

    try:
        opts, args = getopt.getopt(argv,"hm:o:",["message=","ofile="])
    except getopt.GetoptError:
        print ('helloworld.py -message <message> -ofile <outputfile.txt>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ('wilcoxon.py -x <xfile> -y <yfile> -t <tfile> -p <pvfile>')
            sys.exit()
        elif opt in ("-m", "--message"):
            message = arg
        elif opt in ("-o", "--ofile"):
            ofile = arg

    #print("message", message)
    #print("ofile", ofile)

    pvf = open(ofile,'w')
    pvf.write(message)
    pvf.close()

    return 0

if __name__ == "__main__":
   main(sys.argv[1:])    
