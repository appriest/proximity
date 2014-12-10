// This is a parsing file for Pixie output binary files

#include <iostream>
#include <fstream>
#include <string.h>

int main(int argc, char* argv[]){
	
	std::ifstream inFile (argv[1], std::ifstream::binary);  // argv[1] should contain the Pixie file name to be parsed with extension .bin

	if(inFile){
		
		std::ofstream outFile;
		char* fname = argv[1];
		int flen = strlen(argv[1]);
		fname[flen-3] = 't';
		fname[flen-2] = 'x';
		fname[flen-1] = 't';
		
		std::cout << fname << std::endl;

		outFile.open(fname);

		inFile.seekg(0, inFile.end);
		int length = inFile.tellg();
		inFile.seekg(0, inFile.beg);

		char * buffer = new char[length];

		std::cout << "Reading " << length << " characters... ";

		inFile.read(buffer, length);

		if(inFile){
			std::cout << "All characters were read successfully." << std::endl;
		}
		else{
			std::cout << "Error: only " << inFile.gcount() << " characters could be read." << std::endl;
		}

		inFile.close();
		
		outFile << buffer;
		delete[] buffer;

	}

	return 0;

}
