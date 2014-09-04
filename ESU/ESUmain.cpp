// c++ includes
#include <iostream>
#include <vector>
#include <fstream>
#include <string>
#include <stdlib.h>

// ROOT includes
#include <TGraph.h>
#include <TCanvas.h>

using namespace std;

class profile{
	public:

		profile(int p, int s){
			pos = p;
			spread = s;
		}

		int iterate(){
			return pos++;
		}

		int getPos(){
			return pos;
		}
		
		int getSpread(){
			return spread;
		}

	protected:

		int pos;
		int spread;

};

class WP{

	public:

		WP(char* wpFile){
			char str[256];
			ifstream source (wpFile);
			
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
		}

		void plotWP(){
			
			//TCanvas *c1 = new TCanvas("c1", "WeightingPotential");
			int n;
			n = x.size();
			TGraph *gr = new TGraph(n);
			for(int i=0; i<n; i++){
				double x1,y1;
				x1 = x.at(i);
				y1 = wp.at(i);
				gr->SetPoint(i,x1,y1);
			}
			gr->SetTitle("Weighting Potential");
			/*xaxis = gr->GetXaxis();
			xaxis->SetTitle("Position (mm)");
			yaxis = gr->GetYaxis();
			yaxis->SetTitle("Weighting Potential");*/
			gr->Draw();
			cout << "Press ENTER when done." << endl;
			int dummy;
			cin >> dummy;
		}		

	protected:

		vector<float> wp;
		vector<float> x;

};

int main(int argc, char* argv[]){
	
	int initPos = 0;
	int spread = 20;
	//double int2um = 100.0;

	profile p(initPos, spread);	
	cout << "Initial position: " << p.getPos() << endl;
	cout << "Spread: " << p.getSpread() << endl;	
	WP wp1("inFile.txt");
	wp1.plotWP();

	return 0;
}
