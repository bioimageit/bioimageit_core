

macro threshold_particles{

	run("Set Measurements...", "area centroid redirect=None decimal=3");

	// parse args
	args = parseArgs();

	// open the data
	print(args[0])
	open(args[0]);

	// Threshold
	setAutoThreshold(args[1] + " dark");
	print("autothreshold", args[1] + " dark")
	//setOption("BlackBackground", false);
	run("Convert to Mask");

	// analyse particles
	run("Analyze Particles...", "  show=Outlines display clear");
	saveAs("TIFF", args[2]);

	// save the particles count in the file at args[3]
	countFile = File.open(args[3])
	print(countFile, nResults);
	File.close(countFile)

	// save the measurements in file at args[4]
	saveAs("Measurements", args[4]);

}

function parseArgs(){
	argsStr = getArgument()
	print("parse args in args=" + argsStr);
	//argsStr = "[/Users/sprigent/Documents/code/bioimageit/data/explorer/myexperiment/SV_Deconv_2D_8/population1_002_-o.tif,Default dark,/Users/sprigent/Documents/code/bioimageit/data/processes/draw.tif,/Users/sprigent/Documents/code/bioimageit/data/processes/count.csv,/Users/sprigent/Documents/code/bioimageit/data/processes/measures.csv]";
	argsStr = substring(argsStr, 1, lengthOf(argsStr)); // remove first char
	argsStr = substring(argsStr, 0, lengthOf(argsStr)-1); // remove last char
	print(argsStr);
	args = split(argsStr, ",");
	for (i=0 ; i < args.length ; i++){
		print(args[i]);
	}
	return args;
}
