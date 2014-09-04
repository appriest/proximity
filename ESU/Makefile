# Makefile for SIS3302ToROOT parser
# Updated by Micah Folsom 1/6/2014

CC = g++
CCFLAGS = -g -O4 -Wall -std=c++0x -pthread
ROOTLIB := $(shell root-config --glibs)
INC := $(shell root-config --incdir)

EXE = ESUmain 

all: $(EXE)

SIS3302ToROOT: ESUmain.cpp
	$(CC) $(CCFLAGS) -o $@ $^ -I $(INC) $(ROOTLIB)

clean:
	rm $(EXE)
