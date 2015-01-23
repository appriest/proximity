// This is a parsing file for Pixie output binary files

#include <iostream>
#include <fstream>
#include <string.h>

int main(int argc, char* argv[]){
	
	std::ifstream inFile (argv[1], std::ios::binary);  // argv[1] should contain the Pixie file name to be parsed with extension .bin

	if(inFile){
		
		std::ofstream outFile;
		char* fname = argv[1];
		int flen = strlen(argv[1]);
		fname[flen-3] = 't';
		fname[flen-2] = 'x';
		fname[flen-1] = 't';
		
		outFile.open(fname, std::ios::trunc);
		
		std::cout << "Opened output file named: " << fname << std::endl;

		inFile.seekg(0, inFile.end);
		int length = inFile.tellg();
		inFile.seekg(0, inFile.beg);

		const int wordLen = 8;
		
		char * buffer[wordLen];

		//int buffer;

		std::cout << "Reading " << length << " characters... ";

		//for(int loc=0; loc<length; loc += wordLen){
		
		while(inFile.read(reinterpret_cast<char*>(&buffer), wordLen)){

			outFile << buffer << std::endl;
		
		}
		
		if(inFile){
			std::cout << "All characters were read successfully." << std::endl;
		}
		else{
			std::cout << "Error: only " << inFile.gcount() << " characters could be read." << std::endl;
		}

		inFile.close();
		
		//delete[] buffer;

	}

	return 0;

}
