dir = getDirectory("Choose a Directory to PROCESS"); 
list = getFileList(dir);
//Array.sort(list) 
dir2 = getDirectory("Choose a Directory for SAVING"); 
//setBatchMode(true); 
//for (f=0; f<list.length; f++) {
for (f=0; f<2; f++) {
path = dir+list[f]; 
if (!endsWith(path,"/")) {
	s = "open=["+path+"] autoscale color_mode=Grayscale rois_import=[ROI manager] view=Hyperstack stack_order=XYCZT"; 
	run("Bio-Formats Importer", s);
}
if (nImages>=1) {
if (endsWith(path,"f")) {
t=getTitle(); 
s=lastIndexOf(t, '.'); 
t=substring(t, 0,s);
t=replace(t," ","_");
t2= t +' processed';
run("Set Scale...", "known=0.185 distance=1 unit=um"); 
run("DHM 3D show",
      "plotType=3 grid=1024 smooth=6 colorType=3 snapshot=1 rotationZ=-37 rotationX=26 drawText=1 drawLegend=1 drawAxes=0 drawLines=1 perspective=0.1 min=0 max=100 scale=1 scaleZ=0.5 light=0.22 minZSet=-0.15 maxZSet=0.8 isConstantVal=1");
rename(t2); 
saveAs("Tiff", dir2 + t2 + ".tif"); 
run("Close");
run("Close");
}
}
} 