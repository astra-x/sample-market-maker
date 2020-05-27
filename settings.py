import os


RootDir = os.path.dirname(os.path.abspath(__file__))
DataDir=os.path.join(RootDir,"data")

if not os.path.exists(DataDir):
    os.mkdir(DataDir)

S0=200

R=0.05

Sigma = 0.5

T=2

I=1


M=2592000