#include <iostream>
#include <fstream>
#include <string>
#include <stdlib.h>

using namespace std;

int main(){
	
	char fname[] = "inFile.txt";
	char str[256];
	ifstream source (fname);
	
	source.getline(str,256);
	source.getline(str,256);

	while(source.good()){
		source >> str;
		if(!source.good())
			break;
		cout << "x: " << str << "\t";
		source >> str;
		source >> str;
		source >> str;
		cout << "WP: " << str << endl;
	}
	cout << "And that's it!" << endl;
}
