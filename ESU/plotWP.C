#include <vector>
#include <iostream>
#include <cmath>

using namespace std;

void plotWP() {
	TCanvas *c1 = new TCanvas("c1", "WeightingPotential");
	
	vector<float> x,wp;
	char str[256];
	ifstream source ("inFile.txt");
	
	source.getline(str,256);
	source.getline(str,256);
	
	while(source.good()){
		source >> str;
		if(!source.good())
			break;
		//cout << "x: " << str << "\t";
		x.push_back(atof(str));
		source >> str;
		source >> str;
		source >> str;
		//cout << "WP: " << str << endl;
		wp.push_back(atof(str));
	}
	cout << "Position vector size: " << x.size() << endl;
	cout << "WP vector size: " << wp.size() << endl;
	cout << "And that's it!" << endl;
	Int_t n = new Int_t;
	n = x.size();
	TGraph *gr = new TGraph(n);
	for(int i=0; i<n; i++){
		double x1,y1;
		x1 = x.at(i);
		y1 = wp.at(i);
		gr->SetPoint(i,x1,y1);
	}
	gr->SetTitle("Weighting Potential");
	xaxis = gr->GetXaxis();
	xaxis->SetTitle("Position (mm)");
	yaxis = gr->GetYaxis();
	yaxis->SetTitle("Weighting Potential");
	gr->Draw();
}
