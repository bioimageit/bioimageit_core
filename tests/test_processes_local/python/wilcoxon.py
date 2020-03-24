from scipy.stats import wilcoxon
import sys, getopt
from numpy import genfromtxt

def main(argv):

    # parse args
    xfile = ''
    yfile = ''
    tfile = ''
    pvfile = ''

    try:
        opts, args = getopt.getopt(argv,"hx:y:t:p:",["population1=","population2=", "tstat=", "pvalue="])
    except getopt.GetoptError:
        print ('wilcoxon.py -x <xfile> -y <yfile> -t <tfile> -p <pvfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ('wilcoxon.py -x <xfile> -y <yfile> -t <tfile> -p <pvfile>')
            sys.exit()
        elif opt in ("-x", "--population1"):
            xfile = arg
        elif opt in ("-y", "--population2"):
            yfile = arg
        elif opt in ("-t", "--tfile"):
            tfile = arg    
        elif opt in ("-p", "--pvalue"):
            pvfile = arg  

    print("xfile", xfile)
    print("yfile", yfile)

    # read inputs
    x = genfromtxt(xfile, delimiter=',')
    y = genfromtxt(yfile, delimiter=',')

    print("x:", x)
    print("y:", y)


    # run process
    t, p_value = wilcoxon(x, y, zero_method='wilcox', correction=False)
    print('p value', p_value)

    # write outputs
    tf = open(tfile,'w')
    tf.write(str(t))
    tf.close()

    pvf = open(pvfile,'w')
    pvf.write(str(p_value))
    pvf.close()

    return 0

if __name__ == "__main__":
   main(sys.argv[1:])    
