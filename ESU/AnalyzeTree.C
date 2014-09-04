#include "TFile.h"
#include "TTree.h"
#include "TBranch.h"
#include "TTreeReader.h"
#include "TTreeReaderValue.h"

void AnalyzeTree(){
	
	Int_t totalSize = 0;
	//char* fname[] = "
	TFile *f = TFile::Open("http://lcg-heppkg.web.cern.ch/lcg-heppkg/ROOT/eventdata.root");

	if(f == 0){
		cout << "Error: Cannot open file -- " << "http://lcg-heppkg.web.cern.ch/lcg-heppkg/ROOT/eventdata.root" << endl;
		return 1;
	}

	cout << "Successfully opened file -- " <<  "http://lcg-heppkg.web.cern.ch/lcg-heppkg/ROOT/eventdata.root" << endl;
	TTreeReader myReader("EventTree", f);

	TTreeReaderValue<Int_t> eventSize(myReader, "fEventSize");

	while(myReader.Next()){
		totalSize += *eventSize;
	}

	Int_t sizeInMB = totalSize/1024/1024;
	printf("Total size of all events: %d MB", sizeInMB);
}
